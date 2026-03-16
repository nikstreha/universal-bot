import logging
from types import TracebackType

from redis.asyncio import Redis

from src.universal_bot.application.dto.cache.cache_data import CacheDataDTO
from src.universal_bot.application.port.cache.cache_provider import ICacheProvider

logger = logging.getLogger(__name__)


class RedisProvider(ICacheProvider):
    def __init__(self, url: str) -> None:
        self.url = url
        self.redis: Redis | None = None

    async def connect(self) -> None:
        if self.redis is not None:
            return

        self.redis = Redis.from_url(
            url=self.url,
            decode_responses=True,
        )

        try:
            await self.redis.ping()  # pyright: ignore[reportGeneralTypeIssues]
            logger.info("Redis connection established")
        except Exception:
            logger.exception("Redis connection error")

    async def close(self) -> None:
        if self.redis:
            await self.redis.aclose()
            self.redis = None
            logger.info("Redis connection closed")

    async def __aenter__(self) -> RedisProvider:
        await self.connect()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self.close()

    async def get(self, key: str) -> str | None:
        if not self.redis:
            raise RuntimeError("Redis client is not connected. Call connect() first.")

        return await self.redis.get(key)

    async def set(self, cache_data: CacheDataDTO) -> None:
        if not self.redis:
            raise RuntimeError("Redis client is not connected.")

        await self.redis.set(cache_data.key, cache_data.value, ex=cache_data.expire)
