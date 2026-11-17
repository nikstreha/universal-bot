from abc import ABC, abstractmethod

from universal_bot.application.query_model.user import (
    AdminUserQueryModel,
    UserQueryModel,
)
from universal_bot.domain.value_object.user.id import TelegramUserId


class IUserReader(ABC):
    @abstractmethod
    async def find_by_id(self, *, key: TelegramUserId) -> UserQueryModel | None: ...

    @abstractmethod
    async def get_whitelisted_with_usage(
        self, *, admin_id: TelegramUserId
    ) -> list[AdminUserQueryModel]: ...
