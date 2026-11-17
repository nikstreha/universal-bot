import asyncio

from universal_bot.application.port.clock import IClock
from universal_bot.application.port.persistence.file_storage.object_storage import (
    IObjectStorage,
)
from universal_bot.application.port.persistence.repository.job.writer import IJobWriter
from universal_bot.application.port.persistence.repository.stored_file.writer import (
    IStoredFileWriter,
)
from universal_bot.application.port.persistence.repository.verification.writer import (
    IVerificationWriter,
)
from universal_bot.application.port.persistence.uow import IUnitOfWork
from universal_bot.application.service.access.access_policy import AccessPolicy
from universal_bot.domain.common.guard import ensure
from universal_bot.domain.entity.job import Job
from universal_bot.domain.enum.file.state import FileState
from universal_bot.domain.exception.job import LeaseLostError
from universal_bot.domain.value_object.auth.failure_reason import FailureReason
from universal_bot.domain.value_object.file.sha256 import SHA256Digest
from universal_bot.domain.value_object.file.size import FileSize
from universal_bot.domain.value_object.time.timestamp import Timestamp
from universal_bot.domain.value_object.verification.id import VerificationId


class VerifyFileInteractor:
    def __init__(
        self,
        *,
        access_policy: AccessPolicy,
        clock: IClock,
        storage: IObjectStorage,
        stored_file_writer: IStoredFileWriter,
        uow: IUnitOfWork,
        verification_writer: IVerificationWriter,
        job_writer: IJobWriter,
    ) -> None:
        self._access_policy = access_policy
        self._clock = clock
        self._storage = storage
        self._stored_file_writer = stored_file_writer
        self._uow = uow
        self._verification_writer = verification_writer
        self._job_writer = job_writer

    async def __call__(self, *, job: Job) -> None:
        async with self._uow:
            current_job = await self._job_writer.find_by_id(key=job.id_)
            ensure(current_job, LeaseLostError, "Задача не найдена")
            current_job.validate_lease(job.generation, Timestamp(self._clock.now()))
            verification = await self._verification_writer.find_by_id(
                key=VerificationId(job.resource_id.value)
            )
            if verification is None or not verification.start():
                return
            file = await self._stored_file_writer.find_by_id(key=verification.file_id)
            if (
                file is None
                or file.state is not FileState.ACTIVE
                or (not await self._access_policy.allowed(user_id=file.owner_id.value))
            ):
                verification.fail(
                    FailureReason("FILE_UNAVAILABLE"), Timestamp(self._clock.now())
                )
                return
        size, digest, _ = await asyncio.to_thread(
            self._storage.inspect, file.object_key.value
        )
        async with self._uow:
            current_job = await self._job_writer.find_by_id(key=job.id_)
            ensure(current_job, LeaseLostError, "Задача не найдена")
            at = Timestamp(self._clock.now())
            current_job.validate_lease(job.generation, at)
            current = await self._stored_file_writer.find_by_id(key=file.id_)
            check = await self._verification_writer.find_by_id(key=verification.id_)
            if check is None:
                return
            if (
                current is None
                or current.state is not FileState.ACTIVE
                or (
                    not await self._access_policy.allowed(
                        user_id=current.owner_id.value
                    )
                )
            ):
                check.fail(FailureReason("FILE_UNAVAILABLE"), at)
                return
            observed_digest, observed_size = (SHA256Digest(digest), FileSize(size))
            integrity = current.record_integrity(observed_digest, observed_size, at)
            check.record_result(observed_digest, observed_size, integrity, at)
