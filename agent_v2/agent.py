import os
os.environ["OLLAMA_API_BASE"] = "http://localhost:11434"
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from agent_v2.tools import web_search,calculator,code_executor
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters
from google.adk.tools.mcp_tool import McpToolset


root_agent = LlmAgent(
        name="research_agent",
        model=LiteLlm(model="groq/llama-3.3-70b-versatile"),
        description="A research agent that can search the web, do math and execute code.",
        instruction="""You are a helpful research assistant.
        When asked a question:
        - Use web_search for current information or facts
        - Use calculator for any mathematical operations
        - Use code_executor to run Python code when needed
        - Always provide a clear, complete final answer
        """,
        tools=[
            McpToolset(
                connection_params=StdioConnectionParams(
                    server_params=StdioServerParameters(
                        command="python",
                        args=["-m","mcp_server.server"]
                    )
                )
            )
        ]

    )

agent = root_agent



#for websocket
ws_agent = LlmAgent(
        name="research_agent_ws",
        model=LiteLlm(model="groq/llama-3.3-70b-versatile"),
        description="A research agent that can search the web, do math and execute code.",
        instruction="""You are a helpful research assistant.
        When asked a question:
        - Use web_search for current information or facts
        - Use calculator for any mathematical operations
        - Use code_executor to run Python code when needed
        - Always provide a clear, complete final answer
        """,
        tools=[web_search,calculator,code_executor]

    )


