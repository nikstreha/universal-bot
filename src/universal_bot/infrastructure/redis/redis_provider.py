import logging
from types import TracebackType

from redis.asyncio import Redis

from universal_bot.application.dto.cache.cache_data import CacheDataDTO
from universal_bot.application.port.cache.cache_provider import ICacheProvider

logger = logging.getLogger(__name__)


class RedisProvider(ICacheProvider):
    def __init__(self, url: str) -> None:
        self.url = url
        self._redis: Redis | None = None

    @property
    def redis(self) -> Redis:
        if self._redis is None:
            raise RuntimeError("RedisProvider is not connected. Call up() first.")
        return self._redis

    async def up(self) -> None:
        self._redis = Redis.from_url(
            url=self.url,
            decode_responses=True,
        )

        try:
            await self.redis.ping()  # type: ignore
            logger.info("Redis connection established")
        except Exception:
            self._redis = None
            logger.exception("Redis connection error")

    async def down(self) -> None:
        await self.redis.aclose()
        self._redis = None
        logger.info("Redis connection closed")

    async def __aenter__(self) -> RedisProvider:
        await self.up()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self.down()

    async def get(self, key: str) -> str | None:
        return await self.redis.get(key)

    async def set(self, cache_data: CacheDataDTO) -> None:
        await self.redis.set(cache_data.key, cache_data.value, ex=cache_data.expire)

    async def delete(self, key: str) -> None:
        await self.redis.delete(key)

    async def keys(self, pattern: str) -> list[str] | None:
        key_collection = await self.redis.keys(pattern)
        return list(key_collection) if key_collection else None
