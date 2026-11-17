from abc import ABC, abstractmethod

from universal_bot.application.query_model.access_request import AccessRequestQueryModel
from universal_bot.domain.enum.access_request.status import AccessRequestStatus
from universal_bot.domain.value_object.user.id import TelegramUserId


class IAccessRequestReader(ABC):
    @abstractmethod
    async def find_by_user_id(
        self, *, user_id: TelegramUserId
    ) -> AccessRequestQueryModel | None: ...

    @abstractmethod
    async def get_page_by_status(
        self, *, status: AccessRequestStatus, limit: int
    ) -> list[AccessRequestQueryModel]: ...
