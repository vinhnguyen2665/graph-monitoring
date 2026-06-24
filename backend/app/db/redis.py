import redis.asyncio as redis
from app.core.config import settings

# Global Redis connection pool
redis_client = None

async def get_redis_client():
    global redis_client
    if redis_client is None:
        redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            decode_responses=True
        )
    return redis_client
