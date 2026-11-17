from collections.abc import Sequence

from universal_bot.application.port.clock import IClock
from universal_bot.application.port.persistence.repository.job.writer import IJobWriter
from universal_bot.application.port.persistence.uow import IUnitOfWork
from universal_bot.domain.entity.job import Job
from universal_bot.domain.enum.job.kind import JobKind
from universal_bot.domain.value_object.time.timestamp import Timestamp


class ClaimJobInteractor:
    def __init__(
        self, *, clock: IClock, job_writer: IJobWriter, uow: IUnitOfWork
    ) -> None:
        self._clock = clock
        self._job_writer = job_writer
        self._uow = uow

    async def __call__(self, *, kinds: Sequence[str]) -> Job | None:
        async with self._uow:
            job = await self._job_writer.find_next_available(
                kinds=tuple(JobKind(value) for value in kinds),
                at=Timestamp(self._clock.now()),
            )
            if job:
                job.claim(Timestamp(self._clock.now()))
            return job
