from sqlalchemy import select

from universal_bot.application.port.persistence.repository.session.reader import (
    ISessionReader,
)
from universal_bot.application.query_model.session import SessionQueryModel
from universal_bot.domain.common.util import convert_to_primitive
from universal_bot.domain.value_object.auth.token_hash import TokenHash
from universal_bot.domain.value_object.time.timestamp import Timestamp
from universal_bot.domain.value_object.user.id import TelegramUserId
from universal_bot.infrastructure.persistence.sqla.table.session import (
    session_table as table,
)
from universal_bot.infrastructure.persistence.sqla.type import ReaderSession


class SQLASessionReader(ISessionReader):
    def __init__(self, session: ReaderSession) -> None:
        self._session = session

    async def find_by_token_hash(
        self, *, token_hash: TokenHash
    ) -> SessionQueryModel | None:
        token_hash_raw = convert_to_primitive(token_hash)
        statement = select(table)
        statement = statement.where(table.c.token_hash == token_hash_raw)
        row = (await self._session.execute(statement.limit(1))).mappings().first()
        return SessionQueryModel(**row) if row else None

    async def list_by_user_id(
        self, *, user_id: TelegramUserId, revoked_at: Timestamp
    ) -> list[SessionQueryModel]:
        user_id_raw = convert_to_primitive(user_id)
        revoked_at_raw = convert_to_primitive(revoked_at)
        statement = select(table)
        statement = statement.where(
            table.c.user_id == user_id_raw, table.c.revoked_at == revoked_at_raw
        )
        statement = statement.order_by(table.c.last_seen_at.desc())
        return [
            SessionQueryModel(**row)
            for row in (await self._session.execute(statement)).mappings()
        ]
