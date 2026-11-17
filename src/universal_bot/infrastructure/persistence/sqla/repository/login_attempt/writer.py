from sqlalchemy import delete, func, select

from universal_bot.application.port.persistence.repository.login_attempt.writer import (
    ILoginAttemptWriter,
)
from universal_bot.domain.common.util import convert_to_primitive
from universal_bot.domain.entity.login_attempt import LoginAttempt
from universal_bot.domain.value_object.login_attempt.id import LoginAttemptId
from universal_bot.domain.value_object.time.timestamp import Timestamp
from universal_bot.infrastructure.persistence.sqla.table.auth_attempt import (
    auth_attempt_table,
)
from universal_bot.infrastructure.persistence.sqla.type import WriterSession


class SQLALoginAttemptWriter(ILoginAttemptWriter):
    def __init__(self, session: WriterSession) -> None:
        self._session = session

    async def add(self, *, entity: LoginAttempt) -> None:
        self._session.add(entity)
        await self._session.flush()

    async def find_by_id(self, *, key: LoginAttemptId) -> LoginAttempt | None:
        key_raw = convert_to_primitive(key)
        return await self._session.get(LoginAttempt, key_raw)

    async def delete_expired(self, *, at: Timestamp) -> None:
        at_raw = convert_to_primitive(at)
        await self._session.execute(
            delete(LoginAttempt).where(auth_attempt_table.c.expires_at <= at_raw)
        )

    async def count_active(self, *, at: Timestamp) -> int:
        at_raw = convert_to_primitive(at)
        return (
            await self._session.scalar(
                select(func.count())
                .select_from(LoginAttempt)
                .where(auth_attempt_table.c.expires_at > at_raw)
            )
            or 0
        )
