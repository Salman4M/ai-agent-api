import pytest
from agent.graph import agent
from agent.state import AgentState
from core.config import settings

def make_state(question: str) -> AgentState:
    return AgentState(
        question=question,
        messages=[],
        tool_calls=[],
        final_answer=None,
        user_id = 1,
        session_id="test-123",
        steps=0,
        _pending_tool=None   
    )

def test_agent_uses_calculator():
    state=make_state("what is 25 multiplied by 48?")
    result = agent.invoke(state)
    assert result["final_answer"] is not None
    tools_used = [t["tool"] for t in result["tool_calls"]]
    assert "calculator" in tools_used


def test_agent_uses_web_search():
    state=make_state("what is current Python version?")
    result = agent.invoke(state)
    assert result["final_answer"] is not None
    tools_used = [t["tool"] for t in result["tool_calls"]]
    assert "web_search" in tools_used


def test_agent_returns_final_answer():
    state = make_state("what is 10 + 10?")
    result = agent.invoke(state)
    assert result["final_answer"] is not None
    assert len(result["final_answer"]) > 0


def test_agent_returns_tool_calls():
    state = make_state("what is 100 divided by 4?")
    result = agent.invoke(state)
    assert isinstance(result["tool_calls"],list)

def test_agent_at_max_steps():
    state=make_state("what is 2 + 2?")
    result = agent.invoke(state)
    assert result["steps"] <= settings.max_agent_steps

def test_agent_tool_has_correct_structure():
    state = make_state("what is 5 * 5?")
    result = agent.invoke(state)
    for tool_call in result["tool_calls"]:
        assert "tool" in tool_call
        assert "input" in tool_call
        assert "output" in tool_call
