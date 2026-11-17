from abc import ABC, abstractmethod
from collections.abc import Sequence

from universal_bot.domain.entity.admin_notification import AdminNotification
from universal_bot.domain.value_object.notification.event_key import EventKey
from universal_bot.domain.value_object.notification.id import NotificationId


class IAdminNotificationWriter(ABC):
    @abstractmethod
    async def add(self, *, entity: AdminNotification) -> None: ...

    @abstractmethod
    async def find_by_event_key(
        self, *, event_key: EventKey
    ) -> AdminNotification | None: ...

    @abstractmethod
    async def list_by_ids(
        self, *, ids: Sequence[NotificationId]
    ) -> list[AdminNotification]: ...
