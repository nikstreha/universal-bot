from abc import ABC, abstractmethod

from universal_bot.application.dto.cache.cache_data import CacheDataDTO


class ICacheProvider(ABC):
    @abstractmethod
    async def get(self, key: str) -> str | None: ...

    @abstractmethod
    async def set(self, cache_data: CacheDataDTO) -> None: ...

    @abstractmethod
    async def delete(self, key: str) -> None: ...

    @abstractmethod
    async def keys(self, pattern: str) -> list[str] | None: ...
