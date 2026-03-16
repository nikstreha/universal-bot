from abc import ABC, abstractmethod

from src.universal_bot.application.dto.cache.cache_data import CacheDataDTO


class ICacheProvider(ABC):
    @abstractmethod
    async def get(self, key: str) -> str | None: ...

    @abstractmethod
    async def set(self, cache_data: CacheDataDTO) -> None: ...
