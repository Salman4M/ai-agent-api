import json
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, END
from agent.state import AgentState
from agent.tools.calculator import calculator
from agent.tools.web_search import web_search
from agent.tools.code_executor import code_executor
from core.config import settings
from services.memory_service import get_session_messages, save_session_messages
from services.conversation_service import save_conversation

TOOLS = {
    "web_search":web_search,
    "calculator":calculator,
    "code_executor":code_executor
}

TOOL_DESCRIPTIONS = """
You have acccess to these tools:

1.web_search(query: str) - search the internet for current information
2.calculator(expression: str) - safely evaluate math expressions like "2340 * 0.15"
3.code_executor(code: str) - execute the Python code safely and return output

To use a tool, respond ONLY with this exact JSON format:
{
    "tool": "tool_name",
    "input": "tool input here"
}

To give a final answer, respond ONLY with this exact JSON format:
{
    "final_answer": "your complete answer here"    
}

Think step by step. Use tools when you need current information or calculations.
"""

llm = ChatOllama(
    base_url = settings.ollama_base_url,
    model = settings.ollama_model,
    temperature=0
)

def reason(state: AgentState) ->  AgentState:
    messages = [
        {"role":"system", "content":TOOL_DESCRIPTIONS}
    ]
    #conversation history
    messages.extend(state["messages"])

    #if it's the first step , then add the question
    if not state["messages"]:
        messages.append({
            "role":"user",
            "content":state["question"]
        })

    response = llm.invoke(messages)
    content = response.content.strip()

    #against problems in LLM output
    try:
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        #only first json object if llm returned multiple
        if content.count('{') > 1:
            content = content[:content.index('}') + 1]

        parsed = json.loads(content)

        if "final_answer" in parsed:
            return {
                **state,
                "final_answer": parsed["final_answer"],
                "messages":state["messages"] + [
                    {"role":"user","content":state["question"]},
                    {"role":"assistant","content":content}
                ]if not state["messages"] else state["messages"] + [
                    {"role":"assistant","content":content}
                ],
                "steps":state["steps"] + 1,
            }
        
        if "tool" in parsed:
            return {
                **state,
                "messages":state["messages"] + [
                    {"role":"user","content":state["question"]},
                    {"role":"assistant","content":content}
                ]if not state["messages"] else state["messages"] + [
                    {"role":"assistant","content":content}
                ],
                "steps":state["steps"] + 1,
                "_pending_tool": parsed,
            }
    except (json.JSONDecodeError, KeyError):
        return {
            **state,
            "final_answer":content,
            "steps":state["steps"] + 1,
        }
    return {**state, "steps":state["steps"] + 1}
    

def call_tool(state: AgentState) -> AgentState:
    pending = state.get("_pending_tool")
    if not pending:
        return state
    
    tool_name = pending.get("tool")
    tool_input = pending.get("input","")

    if tool_name not in TOOLS:
        tool_output = f"Error: unknown tool '{tool_name}'"
    else:
        tool_output = TOOLS[tool_name](tool_input)

    tool_call = {
        "tool":tool_name,
        "input":tool_input,
        "output":tool_output,
    }
    #add tool result to messages, so llm sees it next step
    tool_message = f"Tool '{tool_name}' returned: {tool_output}"

    return {
        **state,
        "tool_calls":state["tool_calls"] + [tool_call],
        "messages": state["messages"] + [
            {"role":"user","content":tool_message}
        ],
        "_pending_tool":None,
    }

def should_continue(state: AgentState) -> str:
    if state.get("final_answer"):
        return "end"
    if state["steps"] >= settings.max_agent_steps:
        return "end"
    if state.get("_pending_tool"):
        return "call_tool"
    return "end"

def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("reason",reason)
    graph.add_node("call_tool",call_tool)
    
    graph.set_entry_point("reason")
    
    graph.add_conditional_edges(
        "reason",
        should_continue,
        {
            "call_tool":"call_tool",
            "end":END,
        }
    )
    graph.add_edge("call_tool", "reason")
    
    return graph.compile()

agent = build_graph()



async def run_agent(
        question:str,
        user_id:str,
        session_id:str,
        db
)->dict:
    #load session history from Redis (fallback to postgresql)
    messages = await get_session_messages(user_id,session_id,db)

    state = AgentState(
        question = question,
        messages = messages, 
        tool_calls=[],
        final_answer=None,
        user_id = user_id,
        session_id=session_id,
        steps=0,
        _pending_tool = None
    )

    result = agent.invoke(state)

    await save_session_messages(user_id,session_id ,result["messages"])

    await save_conversation(
        db = db,
        user_id = user_id,
        session_id=session_id,
        question=question,
        answer=result["final_answer"] or "",
        steps=result["tool_calls"]
    )
    return result