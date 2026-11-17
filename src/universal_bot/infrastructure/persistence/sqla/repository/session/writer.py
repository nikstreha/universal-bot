from sqlalchemy import select

from universal_bot.application.port.persistence.repository.session.writer import (
    ISessionWriter,
)
from universal_bot.domain.common.util import convert_to_primitive
from universal_bot.domain.entity.session import Session
from universal_bot.domain.value_object.session.id import SessionId
from universal_bot.domain.value_object.time.timestamp import Timestamp
from universal_bot.domain.value_object.user.id import TelegramUserId
from universal_bot.infrastructure.persistence.sqla.table.session import session_table
from universal_bot.infrastructure.persistence.sqla.type import WriterSession


class SQLASessionWriter(ISessionWriter):
    def __init__(self, session: WriterSession) -> None:
        self._session = session

    async def add(self, *, entity: Session) -> None:
        self._session.add(entity)
        await self._session.flush()

    async def find_by_id(self, *, key: SessionId) -> Session | None:
        key_raw = convert_to_primitive(key)
        return await self._session.get(Session, key_raw)

    async def list_by_user_id(
        self, *, user_id: TelegramUserId, revoked_at: Timestamp
    ) -> list[Session]:
        user_id_raw = convert_to_primitive(user_id)
        revoked_at_raw = convert_to_primitive(revoked_at)
        statement = select(Session)
        statement = statement.where(
            session_table.c.user_id == user_id_raw,
            session_table.c.revoked_at == revoked_at_raw,
        )
        return list(await self._session.scalars(statement))
