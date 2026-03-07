from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.conversation import Conversation


async def save_conversation(
        db: AsyncSession,
        user_id: int,
        session_id: str,
        question:str,
        answer: str,
        steps:list[dict]
):
    conversation = Conversation(
        user_id=user_id,
        session_id=session_id,
        question=question,
        answer=answer,
        steps=steps
    )
    db.add(conversation)
    await db.commit()

async def get_recent_conversations(
        db:AsyncSession,
        user_id:int,
        limit:int = 3
) -> list[dict]:
    result = db.execute(
        select(Conversation)
        .where(Conversation.user_id==user_id)
        .order_by(Conversation.created_at.desc())
        .limit(limit)
    )
    conversations = result.scalars().all()
    #converting to message format for llm context
    messages = []
    for conv in reversed(conversations):
        messages.append({"role":"user","content":conv.question})
        messages.append({"role":"assistant","content":conv.answer})
    return messages


async def get_all_conversations(
        db: AsyncSession,
        user_id: int
)->list[Conversation]:
    result = await db.execute(
        select(Conversation)
        .where(Conversation.user_id==user_id)
        .order_by(Conversation.created_at.desc())
    )
    return result.scalars().all()


