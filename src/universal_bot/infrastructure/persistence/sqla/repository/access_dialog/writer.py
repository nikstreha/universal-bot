from universal_bot.application.port.persistence.repository.access_dialog.writer import (
    IAccessDialogWriter,
)
from universal_bot.domain.common.util import convert_to_primitive
from universal_bot.domain.entity.access_dialog import AccessDialog
from universal_bot.domain.value_object.user.id import TelegramUserId
from universal_bot.infrastructure.persistence.sqla.type import WriterSession


class SQLAAccessDialogWriter(IAccessDialogWriter):
    def __init__(self, session: WriterSession) -> None:
        self._session = session

    async def find_by_id(self, *, key: TelegramUserId) -> AccessDialog | None:
        key_raw = convert_to_primitive(key)
        return await self._session.get(AccessDialog, key_raw)

    async def add(self, *, entity: AccessDialog) -> None:
        self._session.add(entity)
        await self._session.flush()

    async def delete(self, *, entity: AccessDialog) -> None:
        await self._session.delete(entity)
