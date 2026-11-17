from universal_bot.application.port.clock import IClock
from universal_bot.application.port.persistence.repository.job.writer import IJobWriter
from universal_bot.application.port.persistence.repository.stored_file.writer import (
    IStoredFileWriter,
)
from universal_bot.application.port.persistence.repository.verification.writer import (
    IVerificationWriter,
)
from universal_bot.application.port.persistence.uow import IUnitOfWork
from universal_bot.application.port.security.secrets import ISecrets
from universal_bot.application.service.access.access_policy import AccessPolicy
from universal_bot.domain.common.guard import ensure
from universal_bot.domain.entity.job import Job
from universal_bot.domain.entity.verification import Verification
from universal_bot.domain.enum.job.kind import JobKind
from universal_bot.domain.exception.common import NotFoundError
from universal_bot.domain.value_object.file.idempotency_key import IdempotencyKey
from universal_bot.domain.value_object.job.id import JobId
from universal_bot.domain.value_object.job.resource_id import ResourceId
from universal_bot.domain.value_object.stored_file.id import StoredFileId
from universal_bot.domain.value_object.time.timestamp import Timestamp
from universal_bot.domain.value_object.user.id import TelegramUserId
from universal_bot.domain.value_object.verification.id import VerificationId


class RequestFileVerificationInteractor:
    def __init__(
        self,
        *,
        secrets: ISecrets,
        uow: IUnitOfWork,
        verification_writer: IVerificationWriter,
        access_policy: AccessPolicy,
        stored_file_writer: IStoredFileWriter,
        clock: IClock,
        job_writer: IJobWriter,
    ) -> None:
        self._secrets = secrets
        self._uow = uow
        self._verification_writer = verification_writer
        self._access_policy = access_policy
        self._stored_file_writer = stored_file_writer
        self._clock = clock
        self._job_writer = job_writer

    async def __call__(self, *, user_id: int, file_id: str, key: str) -> Verification:
        async with self._uow:
            await self._access_policy.require_access(user_id=user_id)
            file = await self._stored_file_writer.find_by_id(key=StoredFileId(file_id))
            ensure(file, NotFoundError, "Файл не найден")
            file.require_owner(TelegramUserId(user_id))
            file.require_active()
            row = await self._verification_writer.find_by_file_id_and_operation_key(
                file_id=StoredFileId(file_id), operation_key=IdempotencyKey(key)
            )
            if row is None:
                row = Verification(
                    id_=VerificationId(self._secrets.identity()),
                    file_id=StoredFileId(file_id),
                    operation_key=IdempotencyKey(key),
                )
                await self._verification_writer.add(entity=row)
                task = Job.create(
                    id_=JobId(self._secrets.identity()),
                    kind=JobKind("verify"),
                    resource_id=ResourceId(str(row.id_.value)),
                    at=Timestamp(self._clock.now()),
                )
                if not await self._job_writer.find_by_dedup_key(
                    dedup_key=task.dedup_key
                ):
                    await self._job_writer.add(entity=task)
            return row
