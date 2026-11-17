from collections.abc import Sequence

from sqlalchemy import or_, select

from universal_bot.application.port.persistence.repository.job.writer import IJobWriter
from universal_bot.domain.common.util import convert_to_primitive
from universal_bot.domain.entity.job import Job
from universal_bot.domain.enum.job.kind import JobKind
from universal_bot.domain.value_object.job.deduplication_key import DeduplicationKey
from universal_bot.domain.value_object.job.id import JobId
from universal_bot.domain.value_object.time.timestamp import Timestamp
from universal_bot.infrastructure.persistence.sqla.table.job import job_table
from universal_bot.infrastructure.persistence.sqla.type import WriterSession


class SQLAJobWriter(IJobWriter):
    def __init__(self, session: WriterSession) -> None:
        self._session = session

    async def find_next_available(
        self, *, kinds: Sequence[JobKind], at: Timestamp
    ) -> Job | None:
        kinds_raw = convert_to_primitive(kinds)
        at_raw = convert_to_primitive(at)
        statement = select(Job).where(
            job_table.c.state.in_(("queued", "running")),
            job_table.c.next_attempt_at <= at_raw,
            or_(job_table.c.state == "queued", job_table.c.lease_until <= at_raw),
        )
        statement = statement.where(job_table.c.kind.in_(kinds_raw))
        statement = statement.order_by(
            job_table.c.next_attempt_at, job_table.c.created_at, job_table.c.id
        ).limit(1)
        return (await self._session.scalars(statement)).first()

    async def find_by_id(self, *, key: JobId) -> Job | None:
        key_raw = convert_to_primitive(key)
        return await self._session.get(Job, key_raw)

    async def find_by_dedup_key(self, *, dedup_key: DeduplicationKey) -> Job | None:
        dedup_key_raw = convert_to_primitive(dedup_key)
        statement = select(Job)
        statement = statement.where(job_table.c.dedup_key == dedup_key_raw)
        return (await self._session.scalars(statement.limit(1))).first()

    async def add(self, *, entity: Job) -> None:
        self._session.add(entity)
        await self._session.flush()
