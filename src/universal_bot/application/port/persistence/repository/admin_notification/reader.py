from abc import ABC, abstractmethod

from universal_bot.application.query_model.admin_notification import (
    AdminNotificationQueryModel,
)


class IAdminNotificationReader(ABC):
    @abstractmethod
    async def get_page(
        self, *, unread: bool, offset: int, limit: int
    ) -> list[AdminNotificationQueryModel]: ...
