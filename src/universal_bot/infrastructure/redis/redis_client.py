import logging

from redis.asyncio import Redis

from universal_bot.composition.configuration.config import settings

logger = logging.getLogger(__name__)


class _RedisClient:
    def __init__(self) -> None:
        self.redis: Redis | None = None

    async def connect(self) -> None:
        if self.redis is not None:
            return

        self.redis = Redis.from_url(
            url=settings.redis_url,
            decode_responses=True,
        )
        try:
            await self.redis.ping()
            logger.info("Redis connection established")
        except Exception:
            logger.exception("Redis connection error")

    async def close(self) -> None:
        if self.redis:
            await self.redis.aclose()
            self.redis = None
            logger.info("Redis connection closed")


_redis_client = _RedisClient()


def get_redis_client() -> _RedisClient:
    return _redis_client
