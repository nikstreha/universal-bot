from sqlalchemy import select

from universal_bot.application.port.persistence.repository.access_request.writer import (
    IAccessRequestWriter,
)
from universal_bot.domain.common.util import convert_to_primitive
from universal_bot.domain.entity.access_request import AccessRequest
from universal_bot.domain.value_object.access_request.id import AccessRequestId
from universal_bot.domain.value_object.user.id import TelegramUserId
from universal_bot.infrastructure.persistence.sqla.table.access_request import (
    access_request_table,
)
from universal_bot.infrastructure.persistence.sqla.type import WriterSession


class SQLAAccessRequestWriter(IAccessRequestWriter):
    def __init__(self, session: WriterSession) -> None:
        self._session = session

    async def find_by_user_id(self, *, user_id: TelegramUserId) -> AccessRequest | None:
        user_id_raw = convert_to_primitive(user_id)
        statement = select(AccessRequest)
        statement = statement.where(access_request_table.c.user_id == user_id_raw)
        return (await self._session.scalars(statement.limit(1))).first()

    async def add(self, *, entity: AccessRequest) -> None:
        self._session.add(entity)
        await self._session.flush()

    async def find_by_id(self, *, key: AccessRequestId) -> AccessRequest | None:
        key_raw = convert_to_primitive(key)
        return await self._session.get(AccessRequest, key_raw)
