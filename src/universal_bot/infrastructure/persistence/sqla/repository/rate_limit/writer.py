from sqlalchemy import delete

from universal_bot.application.port.persistence.repository.rate_limit.writer import (
    IRateLimitWriter,
)
from universal_bot.domain.common.util import convert_to_primitive
from universal_bot.domain.entity.rate_limit import RateLimit
from universal_bot.domain.value_object.rate_limit.key import RateLimitKey
from universal_bot.domain.value_object.time.timestamp import Timestamp
from universal_bot.infrastructure.persistence.sqla.table.rate_limit import (
    rate_limit_table,
)
from universal_bot.infrastructure.persistence.sqla.type import WriterSession


class SQLARateLimitWriter(IRateLimitWriter):
    def __init__(self, session: WriterSession) -> None:
        self._session = session

    async def find_by_id(self, *, key: RateLimitKey) -> RateLimit | None:
        key_raw = convert_to_primitive(key)
        return await self._session.get(RateLimit, key_raw)

    async def add(self, *, entity: RateLimit) -> None:
        self._session.add(entity)
        await self._session.flush()

    async def delete_stale(self, *, before: Timestamp) -> None:
        before_raw = convert_to_primitive(before)
        await self._session.execute(
            delete(RateLimit).where(rate_limit_table.c.window_start <= before_raw)
        )
