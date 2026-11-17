from abc import ABC, abstractmethod

from universal_bot.domain.entity.access_grant import AccessGrant
from universal_bot.domain.value_object.user.id import TelegramUserId


class IAccessGrantWriter(ABC):
    @abstractmethod
    async def find_by_id(self, *, key: TelegramUserId) -> AccessGrant | None: ...

    @abstractmethod
    async def add(self, *, entity: AccessGrant) -> None: ...

    @abstractmethod
    async def delete(self, *, entity: AccessGrant) -> None: ...
