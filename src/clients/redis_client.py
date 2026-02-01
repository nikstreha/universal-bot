import logging
from typing import Optional

from redis.asyncio import Redis
from src.core.config import settings

logger = logging.getLogger(__name__)

class RedisClient:
    def __init__(self):
        self.redis: Optional[Redis] = None

    async def connect(self):
        self.redis = Redis.from_url(url=settings.redis_url, decode_responses=True)
        try:
            await self.redis.ping()
            logger.info("Redis connection established")
        except Exception as e:
            logger.error("Redis connection error: %s", e)
            raise ConnectionError(f"Cannot connect to Redis: {e}")

    async def close(self):
        if self.redis:
            await self.redis.aclose()
            self.redis = None
            logger.info("Redis connection closed")


redis_client = RedisClient()
