from abc import ABC, abstractmethod

from universal_bot.domain.entity.user import User
from universal_bot.domain.value_object.user.id import TelegramUserId


class IUserWriter(ABC):
    @abstractmethod
    async def find_by_id(self, *, key: TelegramUserId) -> User | None: ...

    @abstractmethod
    async def add(self, *, entity: User) -> None: ...
