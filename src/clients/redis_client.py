from typing import Optional

from redis.asyncio import Redis

from src.core.config import settings

class RedisClient:
    def __init__(self):
        self.redis: Optional[Redis] = None

    async def connect(self):
        self.redis = Redis.from_url(url=settings.redis_url, decode_responses=True)
        try:
            await self.redis.ping()
        except Exception as e:
            raise ConnectionError(f"Cannot connect to Redis: {e}")

    async def close(self):
        if self.redis:
            await self.redis.aclose()
            self.redis = None
