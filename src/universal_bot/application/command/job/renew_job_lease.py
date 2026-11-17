from universal_bot.application.port.clock import IClock
from universal_bot.application.port.persistence.repository.job.writer import IJobWriter
from universal_bot.application.port.persistence.uow import IUnitOfWork
from universal_bot.domain.common.guard import ensure
from universal_bot.domain.entity.job import Job
from universal_bot.domain.exception.job import LeaseLostError
from universal_bot.domain.value_object.time.timestamp import Timestamp


class RenewJobLeaseInteractor:
    def __init__(
        self, *, clock: IClock, uow: IUnitOfWork, job_writer: IJobWriter
    ) -> None:
        self._clock = clock
        self._uow = uow
        self._job_writer = job_writer

    async def __call__(self, *, job: Job) -> None:
        async with self._uow:
            fresh = await self._job_writer.find_by_id(key=job.id_)
            ensure(fresh, LeaseLostError, "Задача не найдена")
            fresh.validate_lease(job.generation, Timestamp(self._clock.now()))
            fresh.renew(job.generation, Timestamp(self._clock.now()))
