from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from core.security import get_current_user
from models.conversation import User
from schemas.agent import AgentRequest, AgentResponse, HistoryItem,HistoryResponse,ToolStep
from services.session_service import generate_session_id
from services.conversation_service import get_all_conversations
from agent.graph import run_agent

router=APIRouter(prefix="/agent",tags=["agent"])

@router.post("/run",response_model=AgentResponse)
async def run(
    request:AgentRequest,
    current_user: User = Depends(get_current_user),
    db:AsyncSession = Depends(get_db)
):
    session_id = generate_session_id()
    
    result = await run_agent(
        question=request.question,
        user_id = current_user.id,
        session_id = session_id,
        db=db
    )
    if not result["final_answer"]:
        raise HTTPException(status_code=500,detail="Agent failed to prdouce an answer")
    
    answer = result["final_answer"]
    if '{"final_answer"' in answer:
        answer = answer.split('{"final_answer"')[0].strip()
    return AgentResponse(
        answer=answer,
        steps=[
            ToolStep(
                tool=t["tool"],
                input=t["input"],
                output=t["output"]
            )
            for t in result["tool_calls"]
        ],
        session_id = session_id
    )


@router.get("/history",response_model=HistoryResponse)
async def history(
    current_user: User = Depends(get_current_user),
    db:AsyncSession = Depends(get_db)
):
    conversations = await get_all_conversations(db,current_user.id)
    return HistoryResponse(
        sessions=[
            HistoryItem(
                session_id=c.session_id,
                question=c.question,
                answer=c.answer,
                steps=c.steps,
                created_at=c.created_at
            )
            for c in conversations
        ]
    )


