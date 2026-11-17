from abc import ABC, abstractmethod

from universal_bot.application.query_model.access_grant import AccessGrantQueryModel
from universal_bot.domain.value_object.user.id import TelegramUserId


class IAccessGrantReader(ABC):
    @abstractmethod
    async def find_by_id(
        self, *, key: TelegramUserId
    ) -> AccessGrantQueryModel | None: ...
