from abc import ABC, abstractmethod

from universal_bot.domain.entity.login_attempt import LoginAttempt
from universal_bot.domain.value_object.login_attempt.id import LoginAttemptId
from universal_bot.domain.value_object.time.timestamp import Timestamp


class ILoginAttemptWriter(ABC):
    @abstractmethod
    async def add(self, *, entity: LoginAttempt) -> None: ...

    @abstractmethod
    async def find_by_id(self, *, key: LoginAttemptId) -> LoginAttempt | None: ...

    @abstractmethod
    async def delete_expired(self, *, at: Timestamp) -> None: ...

    @abstractmethod
    async def count_active(self, *, at: Timestamp) -> int: ...
