from abc import ABC, abstractmethod

from universal_bot.domain.entity.session import Session
from universal_bot.domain.value_object.session.id import SessionId
from universal_bot.domain.value_object.time.timestamp import Timestamp
from universal_bot.domain.value_object.user.id import TelegramUserId


class ISessionWriter(ABC):
    @abstractmethod
    async def add(self, *, entity: Session) -> None: ...

    @abstractmethod
    async def find_by_id(self, *, key: SessionId) -> Session | None: ...

    @abstractmethod
    async def list_by_user_id(
        self, *, user_id: TelegramUserId, revoked_at: Timestamp
    ) -> list[Session]: ...
