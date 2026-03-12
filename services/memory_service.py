import json
from core.redis import get_redis
from core.config import settings
from services.conversation_service import get_recent_conversations

async def get_session_messages(user_id: int, session_id:str,db=None)->list[dict]:
    redis = await get_redis()
    key = f"session:{user_id}:{session_id}"
    data = await redis.get(key)
    if not data:
        #redis expired , load context from postgesql if db provided
        if db:
            return await get_recent_conversations(db,user_id,limit=3)
        return []
    return json.loads(data)

async def save_session_messages(user_id:int, session_id:str, messages:list[dict]):
    redis = await get_redis()
    key = f"session:{user_id}:{session_id}"
    await redis.set(key,json.dumps(messages),ex=settings.session_ttl_seconds)


async def delete_session(user_id: int, session_id:str):
    redis = await get_redis()
    key = f"session:{user_id}:{session_id}"
    await redis.delete(key)