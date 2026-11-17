from sqlalchemy import select

from universal_bot.application.port.persistence.repository.admin_notification.reader import (
    IAdminNotificationReader,
)
from universal_bot.application.query_model.admin_notification import (
    AdminNotificationQueryModel,
)
from universal_bot.infrastructure.persistence.sqla.table.admin_notification import (
    admin_notification_table as table,
)
from universal_bot.infrastructure.persistence.sqla.type import ReaderSession


class SQLAAdminNotificationReader(IAdminNotificationReader):
    def __init__(self, session: ReaderSession) -> None:
        self._session = session

    async def get_page(
        self, *, unread: bool, offset: int, limit: int
    ) -> list[AdminNotificationQueryModel]:
        statement = select(table)
        if unread:
            statement = statement.where(table.c.read_at.is_(None))
        statement = (
            statement.order_by(table.c.created_at.desc(), table.c.id)
            .offset(offset)
            .limit(limit)
        )
        return [
            AdminNotificationQueryModel(**row)
            for row in (await self._session.execute(statement)).mappings()
        ]
