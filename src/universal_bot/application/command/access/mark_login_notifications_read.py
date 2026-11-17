from collections.abc import Sequence

from universal_bot.application.port.clock import IClock
from universal_bot.application.port.persistence.repository.admin_notification.writer import (
    IAdminNotificationWriter,
)
from universal_bot.application.port.persistence.uow import IUnitOfWork
from universal_bot.application.service.access.access_policy import AccessPolicy
from universal_bot.domain.value_object.notification.id import NotificationId
from universal_bot.domain.value_object.time.timestamp import Timestamp


class MarkLoginNotificationsReadInteractor:
    def __init__(
        self,
        *,
        access_policy: AccessPolicy,
        admin_notification_writer: IAdminNotificationWriter,
        clock: IClock,
        uow: IUnitOfWork,
    ) -> None:
        self._access_policy = access_policy
        self._admin_notification_writer = admin_notification_writer
        self._clock = clock
        self._uow = uow

    async def __call__(self, *, actor_id: int, ids: Sequence[str]) -> None:
        await self._access_policy.require_admin(actor_id=actor_id)
        async with self._uow:
            for row in await self._admin_notification_writer.list_by_ids(
                ids=tuple(NotificationId(value) for value in ids)
            ):
                row.mark_read(Timestamp(self._clock.now()))
