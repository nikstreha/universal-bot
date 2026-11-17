from abc import ABC, abstractmethod

from universal_bot.domain.entity.telegram_update import TelegramUpdate
from universal_bot.domain.value_object.messaging.update_id import TelegramUpdateId


class ITelegramUpdateWriter(ABC):
    @abstractmethod
    async def find_by_id(self, *, key: TelegramUpdateId) -> TelegramUpdate | None: ...

    @abstractmethod
    async def add(self, *, entity: TelegramUpdate) -> None: ...
