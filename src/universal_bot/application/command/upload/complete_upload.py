from universal_bot.application.port.clock import IClock
from universal_bot.application.port.persistence.repository.job.writer import IJobWriter
from universal_bot.application.port.persistence.repository.upload.writer import (
    IUploadWriter,
)
from universal_bot.application.port.persistence.repository.upload_part.writer import (
    IUploadPartWriter,
)
from universal_bot.application.port.persistence.uow import IUnitOfWork
from universal_bot.application.port.security.secrets import ISecrets
from universal_bot.application.service.access.access_policy import AccessPolicy
from universal_bot.domain.common.guard import ensure
from universal_bot.domain.entity.job import Job
from universal_bot.domain.enum.job.kind import JobKind
from universal_bot.domain.exception.common import NotFoundError
from universal_bot.domain.value_object.file.size import FileSize
from universal_bot.domain.value_object.job.id import JobId
from universal_bot.domain.value_object.job.resource_id import ResourceId
from universal_bot.domain.value_object.time.timestamp import Timestamp
from universal_bot.domain.value_object.upload.id import UploadId
from universal_bot.domain.value_object.user.id import TelegramUserId


class CompleteUploadInteractor:
    def __init__(
        self,
        *,
        clock: IClock,
        uow: IUnitOfWork,
        upload_part_writer: IUploadPartWriter,
        job_writer: IJobWriter,
        secrets: ISecrets,
        access_policy: AccessPolicy,
        upload_writer: IUploadWriter,
    ) -> None:
        self._clock = clock
        self._uow = uow
        self._upload_part_writer = upload_part_writer
        self._job_writer = job_writer
        self._secrets = secrets
        self._access_policy = access_policy
        self._upload_writer = upload_writer

    async def __call__(self, *, user_id: int, upload_id: str) -> None:
        async with self._uow:
            await self._access_policy.require_access(user_id=user_id)
            row = await self._upload_writer.find_by_id(key=UploadId(upload_id))
            ensure(row, NotFoundError, "Загрузка не найдена")
            row.require_owner(TelegramUserId(user_id))
            row.expire(Timestamp(self._clock.now()))
            parts = await self._upload_part_writer.list_by_upload_id(upload_id=row.id_)
            if row.verify(
                len(parts),
                FileSize(sum(part.size_bytes.value for part in parts)),
                Timestamp(self._clock.now()),
            ):
                task = Job.create(
                    id_=JobId(self._secrets.identity()),
                    kind=JobKind.FINALIZE,
                    resource_id=ResourceId(row.id_.value),
                    at=Timestamp(self._clock.now()),
                )
                await self._job_writer.add(entity=task)
