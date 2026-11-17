from sqlalchemy import select

from universal_bot.application.port.persistence.repository.access_request.reader import (
    IAccessRequestReader,
)
from universal_bot.application.query_model.access_request import AccessRequestQueryModel
from universal_bot.domain.common.util import convert_to_primitive
from universal_bot.domain.enum.access_request.status import AccessRequestStatus
from universal_bot.domain.value_object.user.id import TelegramUserId
from universal_bot.infrastructure.persistence.sqla.table.access_request import (
    access_request_table as table,
)
from universal_bot.infrastructure.persistence.sqla.type import ReaderSession


class SQLAAccessRequestReader(IAccessRequestReader):
    def __init__(self, session: ReaderSession) -> None:
        self._session = session

    async def find_by_user_id(
        self, *, user_id: TelegramUserId
    ) -> AccessRequestQueryModel | None:
        user_id_raw = convert_to_primitive(user_id)
        statement = select(table)
        statement = statement.where(table.c.user_id == user_id_raw)
        row = (await self._session.execute(statement.limit(1))).mappings().first()
        return AccessRequestQueryModel(**row) if row else None

    async def get_page_by_status(
        self, *, status: AccessRequestStatus, limit: int
    ) -> list[AccessRequestQueryModel]:
        status_raw = convert_to_primitive(status)
        statement = select(table)
        statement = statement.where(table.c.status == status_raw)
        statement = statement.order_by(table.c.created_at.desc(), table.c.id)
        statement = statement.limit(limit)
        return [
            AccessRequestQueryModel(**row)
            for row in (await self._session.execute(statement)).mappings()
        ]
