from typing import TypedDict

class ToolCall(TypedDict):
    tool: str
    input: str
    output: str

class AgentState(TypedDict):
    question:str
    messages: list[dict]
    tool_calls: list[ToolCall]
    final_answer: str | None
    user_id: int
    session_id: str
    steps: int
    _pending_tool: dict | None
