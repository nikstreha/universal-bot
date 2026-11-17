from sqlalchemy import select

from universal_bot.application.port.persistence.repository.access_grant.reader import (
    IAccessGrantReader,
)
from universal_bot.application.query_model.access_grant import AccessGrantQueryModel
from universal_bot.domain.common.util import convert_to_primitive
from universal_bot.domain.value_object.user.id import TelegramUserId
from universal_bot.infrastructure.persistence.sqla.table.whitelist import (
    whitelist_table as table,
)
from universal_bot.infrastructure.persistence.sqla.type import ReaderSession


class SQLAAccessGrantReader(IAccessGrantReader):
    def __init__(self, session: ReaderSession) -> None:
        self._session = session

    async def find_by_id(self, *, key: TelegramUserId) -> AccessGrantQueryModel | None:
        key_raw = convert_to_primitive(key)
        row = (
            (
                await self._session.execute(
                    select(table).where(table.c.user_id == key_raw).limit(1)
                )
            )
            .mappings()
            .first()
        )
        return AccessGrantQueryModel(**row) if row else None
