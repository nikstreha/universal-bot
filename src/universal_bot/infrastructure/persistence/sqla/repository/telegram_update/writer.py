from universal_bot.application.port.persistence.repository.telegram_update.writer import (
    ITelegramUpdateWriter,
)
from universal_bot.domain.common.util import convert_to_primitive
from universal_bot.domain.entity.telegram_update import TelegramUpdate
from universal_bot.domain.value_object.messaging.update_id import TelegramUpdateId
from universal_bot.infrastructure.persistence.sqla.type import WriterSession


class SQLATelegramUpdateWriter(ITelegramUpdateWriter):
    def __init__(self, session: WriterSession) -> None:
        self._session = session

    async def find_by_id(self, *, key: TelegramUpdateId) -> TelegramUpdate | None:
        key_raw = convert_to_primitive(key)
        return await self._session.get(TelegramUpdate, key_raw)

    async def add(self, *, entity: TelegramUpdate) -> None:
        self._session.add(entity)
        await self._session.flush()
