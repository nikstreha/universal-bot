from abc import ABC, abstractmethod

from universal_bot.domain.entity.rate_limit import RateLimit
from universal_bot.domain.value_object.rate_limit.key import RateLimitKey
from universal_bot.domain.value_object.time.timestamp import Timestamp


class IRateLimitWriter(ABC):
    @abstractmethod
    async def find_by_id(self, *, key: RateLimitKey) -> RateLimit | None: ...

    @abstractmethod
    async def add(self, *, entity: RateLimit) -> None: ...

    @abstractmethod
    async def delete_stale(self, *, before: Timestamp) -> None: ...
