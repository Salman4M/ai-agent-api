import redis.asyncio as aioredis
from core.config import settings

redis_client = None

async def get_redis():
    global redis_client
    if redis_client is None:
        redis_client = aioredis.from_url(
            settings.redis_url,
            encoding ="utf-8",
            decode_responses=True
        )
    return redis_client