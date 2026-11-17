from universal_bot.application.port.persistence.repository.access_grant.writer import (
    IAccessGrantWriter,
)
from universal_bot.domain.common.util import convert_to_primitive
from universal_bot.domain.entity.access_grant import AccessGrant
from universal_bot.domain.value_object.user.id import TelegramUserId
from universal_bot.infrastructure.persistence.sqla.type import WriterSession


class SQLAAccessGrantWriter(IAccessGrantWriter):
    def __init__(self, session: WriterSession) -> None:
        self._session = session

    async def find_by_id(self, *, key: TelegramUserId) -> AccessGrant | None:
        key_raw = convert_to_primitive(key)
        return await self._session.get(AccessGrant, key_raw)

    async def add(self, *, entity: AccessGrant) -> None:
        self._session.add(entity)
        await self._session.flush()

    async def delete(self, *, entity: AccessGrant) -> None:
        await self._session.delete(entity)
