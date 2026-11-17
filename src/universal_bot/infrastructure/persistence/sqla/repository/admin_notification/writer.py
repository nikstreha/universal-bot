from collections.abc import Sequence

from sqlalchemy import select

from universal_bot.application.port.persistence.repository.admin_notification.writer import (
    IAdminNotificationWriter,
)
from universal_bot.domain.common.util import convert_to_primitive
from universal_bot.domain.entity.admin_notification import AdminNotification
from universal_bot.domain.value_object.notification.event_key import EventKey
from universal_bot.domain.value_object.notification.id import NotificationId
from universal_bot.infrastructure.persistence.sqla.table.admin_notification import (
    admin_notification_table,
)
from universal_bot.infrastructure.persistence.sqla.type import WriterSession


class SQLAAdminNotificationWriter(IAdminNotificationWriter):
    def __init__(self, session: WriterSession) -> None:
        self._session = session

    async def add(self, *, entity: AdminNotification) -> None:
        self._session.add(entity)
        await self._session.flush()

    async def find_by_event_key(
        self, *, event_key: EventKey
    ) -> AdminNotification | None:
        event_key_raw = convert_to_primitive(event_key)
        statement = select(AdminNotification)
        statement = statement.where(
            admin_notification_table.c.event_key == event_key_raw
        )
        return (await self._session.scalars(statement.limit(1))).first()

    async def list_by_ids(
        self, *, ids: Sequence[NotificationId]
    ) -> list[AdminNotification]:
        ids_raw = convert_to_primitive(ids)
        statement = select(AdminNotification)
        statement = statement.where(admin_notification_table.c.id.in_(ids_raw))
        return list(await self._session.scalars(statement))
