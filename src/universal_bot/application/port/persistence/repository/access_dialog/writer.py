from abc import ABC, abstractmethod

from universal_bot.domain.entity.access_dialog import AccessDialog
from universal_bot.domain.value_object.user.id import TelegramUserId


class IAccessDialogWriter(ABC):
    @abstractmethod
    async def find_by_id(self, *, key: TelegramUserId) -> AccessDialog | None: ...

    @abstractmethod
    async def add(self, *, entity: AccessDialog) -> None: ...

    @abstractmethod
    async def delete(self, *, entity: AccessDialog) -> None: ...
