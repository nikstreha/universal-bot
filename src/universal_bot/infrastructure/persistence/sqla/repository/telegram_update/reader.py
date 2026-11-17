from sqlalchemy import select

from universal_bot.application.port.persistence.repository.telegram_update.reader import (
    ITelegramUpdateReader,
)
from universal_bot.application.query_model.telegram_update import (
    TelegramUpdateQueryModel,
)
from universal_bot.domain.common.util import convert_to_primitive
from universal_bot.domain.enum.telegram_update.state import TelegramUpdateState
from universal_bot.infrastructure.persistence.sqla.table.telegram_update import (
    telegram_update_table as table,
)
from universal_bot.infrastructure.persistence.sqla.type import ReaderSession


class SQLATelegramUpdateReader(ITelegramUpdateReader):
    def __init__(self, session: ReaderSession) -> None:
        self._session = session

    async def get_page_by_state(
        self, *, state: TelegramUpdateState, limit: int
    ) -> list[TelegramUpdateQueryModel]:
        state_raw = convert_to_primitive(state)
        statement = select(table)
        statement = statement.where(table.c.state == state_raw)
        statement = statement.order_by(table.c.id)
        statement = statement.limit(limit)
        return [
            TelegramUpdateQueryModel(**row)
            for row in (await self._session.execute(statement)).mappings()
        ]
