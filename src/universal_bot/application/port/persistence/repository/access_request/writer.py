from abc import ABC, abstractmethod

from universal_bot.domain.entity.access_request import AccessRequest
from universal_bot.domain.value_object.access_request.id import AccessRequestId
from universal_bot.domain.value_object.user.id import TelegramUserId


class IAccessRequestWriter(ABC):
    @abstractmethod
    async def find_by_user_id(
        self, *, user_id: TelegramUserId
    ) -> AccessRequest | None: ...

    @abstractmethod
    async def add(self, *, entity: AccessRequest) -> None: ...

    @abstractmethod
    async def find_by_id(self, *, key: AccessRequestId) -> AccessRequest | None: ...
