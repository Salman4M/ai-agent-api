import os
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from agent_v2.tools import web_search,calculator,code_executor

def create_agent()->Agent:
    return Agent(
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
        tools=[web_search,calculator,code_executor]

    )

agent = create_agent()

root_agent = agent