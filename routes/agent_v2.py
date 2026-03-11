from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from google.adk.runners import InMemoryRunner
from google.genai.types import Content,Part

from core.database import get_db
from core.security import get_current_user
from models.conversation import User
from schemas.agent import AgentRequest,AgentResponse,ToolStep
from services.session_service import generate_session_id
from agent_v2.agent import agent


router = APIRouter(prefix="/v2/agent",tags=["agent-v2"])

runner = InMemoryRunner(agent=agent, app_name="ai_agent")

@router.post("/run",response_model=AgentResponse)
async def run(
    request: AgentRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    session_id = generate_session_id()

    session = await runner.session_service.create_session(
        app_name = "ai_agent",
        user_id = str(current_user.id)
    )

    final_answer = None
    async for event in runner.run_async(
        user_id=str(current_user.id),
        session_id=session.id,
        new_message=Content(
            role="user",
            parts=[Part(text=request.question)]
        )
    ):
        if event.is_final_response():
            final_answer = event.content.parts[0].text
    
    if not final_answer:
        raise HTTPException(status_code=500, detail="Agent failed to produce an answer.")
    
    return AgentResponse(
        answer=final_answer,
        steps=[],
        session_id=session_id
    )