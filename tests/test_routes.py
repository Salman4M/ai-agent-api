import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch
from main import app
from core.security import get_current_user
from core.database import get_db
from models.conversation import User
from datetime import datetime

client = TestClient(app)

fake_user = MagicMock()
fake_user.id = 1
fake_user.username = "testuser"
fake_user.email = "test@test.com"
fake_user.created_at = datetime.utcnow()

def get_fake_db():
    return AsyncMock()

@pytest.fixture(autouse=True)
def override_dependices():
    app.dependency_overrides[get_current_user] = lambda: fake_user
    app.dependency_overrides[get_db] = get_fake_db
    yield
    app.dependency_overrides.clear()

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status":"ok"}

def test_run_requires_auth():
    app.dependency_overrides.clear()
    response = client.post("/agent/run",json={"question":"test"})
    assert response.status_code == 401

def test_history_requires_auth():
    app.dependency_overrides.clear()
    response = client.get("/agent/history")
    assert response.status_code == 401

def test_run_with_mock_agent():
    mock_result = {
        "final_answer":"The answer is 42.",
        "tool_calls":[
            {"tool":"calculator","input":"6 * 7","output":"42"}
        ],
        "messages":[],
        "steps":1,
    }
    with patch("routes.agent.run_agent", new = AsyncMock(return_value=mock_result)):
        response = client.post(
            "/agent/run",
            json = {"question":"what is 6 times 7?"}
        )
    assert response.status_code == 200
    data = response.json()
    assert data["answer"]=="The answer is 42."
    assert len(data["steps"]) == 1
    assert data["steps"][0]["tool"] == "calculator"
    assert "session_id" in data


def test_history_with_mock_db():
    mock_conv = MagicMock()
    mock_conv.session_id = "abc-123"
    mock_conv.question = "test question"
    mock_conv.answer = "test answer"
    mock_conv.steps = []
    mock_conv.created_at = datetime.utcnow()

    with patch(
        "routes.agent.get_all_conversations",
        new=AsyncMock(return_value=[mock_conv])
    ):
        response = client.get("/agent/history")

    assert response.status_code == 200
    data = response.json()
    assert len(data["sessions"]) == 1
    assert data["sessions"][0]["question"] == "test question"


def test_run_empty_question():
    mock_result = {
        "final_answer":None,
        "tool_calls": [],
        "messages":[],
        "steps":0
    }
    
    with patch("routes.agent.run_agent", new=AsyncMock(return_value=mock_result)):
        response = client.post(
            "/agent/run",
            json={
                "question":"test"
            }
        )
    assert response.status_code == 500


