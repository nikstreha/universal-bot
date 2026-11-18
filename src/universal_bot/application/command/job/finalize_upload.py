import asyncio

from universal_bot.application.exception.common import UploadCancelledError
from universal_bot.application.port.clock import IClock
from universal_bot.application.port.media.inspector import IMediaInspector
from universal_bot.application.port.persistence.file_storage.object_storage import (
    IObjectStorage,
)
from universal_bot.application.port.persistence.repository.job.writer import IJobWriter
from universal_bot.application.port.persistence.repository.stored_file.writer import (
    IStoredFileWriter,
)
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
from universal_bot.domain.entity.stored_file import StoredFile
from universal_bot.domain.enum.file.media_kind import MediaKind
from universal_bot.domain.enum.job.kind import JobKind
from universal_bot.domain.enum.upload.state import UploadState
from universal_bot.domain.exception.job import LeaseLostError
from universal_bot.domain.value_object.file.mime_type import MimeType
from universal_bot.domain.value_object.file.object_key import ObjectKey
from universal_bot.domain.value_object.file.sha256 import SHA256Digest
from universal_bot.domain.value_object.file.size import FileSize
from universal_bot.domain.value_object.job.id import JobId
from universal_bot.domain.value_object.job.resource_id import ResourceId
from universal_bot.domain.value_object.stored_file.id import StoredFileId
from universal_bot.domain.value_object.time.timestamp import Timestamp
from universal_bot.domain.value_object.upload.id import UploadId


class FinalizeUploadInteractor:
    def __init__(
        self,
        *,
        access_policy: AccessPolicy,
        clock: IClock,
        inspector: IMediaInspector,
        secrets: ISecrets,
        storage: IObjectStorage,
        stored_file_writer: IStoredFileWriter,
        uow: IUnitOfWork,
        upload_part_writer: IUploadPartWriter,
        upload_writer: IUploadWriter,
        job_writer: IJobWriter,
    ) -> None:
        self._access_policy = access_policy
        self._clock = clock
        self._inspector = inspector
        self._secrets = secrets
        self._storage = storage
        self._stored_file_writer = stored_file_writer
        self._uow = uow
        self._upload_part_writer = upload_part_writer
        self._upload_writer = upload_writer
        self._job_writer = job_writer

    async def __call__(self, *, job: Job) -> None:
        async with self._uow:
            current_job = await self._job_writer.find_by_id(key=job.id_)
            ensure(current_job, LeaseLostError, "Задача не найдена")
            current_job.validate_lease(job.generation, Timestamp(self._clock.now()))
            upload = await self._upload_writer.find_by_id(
                key=UploadId(str(job.resource_id.value))
            )
            if (
                not upload
                or upload.state is not UploadState.VERIFYING
                or (
                    not await self._access_policy.allowed(user_id=upload.owner_id.value)
                )
            ):
                return
            parts = await self._upload_part_writer.list_by_upload_id(
                upload_id=upload.id_
            )
        key = upload.original_key(job.generation).value
        await self._storage.ready()
        await self._storage.guard(upload.size_bytes.value)
        await self._storage.compose(key, [p.object_key.value for p in parts])
        size, sha256, header = await self._storage.inspect(key=key)
        kind, mime = await asyncio.to_thread(self._inspector.classify, header)
        async with self._uow:
            current_job = await self._job_writer.find_by_id(key=job.id_)
            ensure(current_job, LeaseLostError, "Задача не найдена")
            current_job.validate_lease(job.generation, Timestamp(self._clock.now()))
            fresh = await self._upload_writer.find_by_id(key=upload.id_)
            ensure(
                fresh is not None
                and fresh.state is UploadState.VERIFYING
                and await self._access_policy.allowed(user_id=fresh.owner_id.value),
                UploadCancelledError,
                "Загрузка остановлена",
            )
            file = StoredFile.from_upload(
                id_=StoredFileId(self._secrets.identity()),
                upload=fresh,
                object_key=ObjectKey(key),
                observed_size=FileSize(size),
                observed_digest=SHA256Digest(sha256),
                mime=MimeType(mime),
                media_kind=MediaKind(kind),
                at=Timestamp(self._clock.now()),
            )
            await self._stored_file_writer.add(entity=file)
            fresh.complete(file.id_)
            if kind in ("photo", "video"):
                task = Job.create(
                    id_=JobId(self._secrets.identity()),
                    kind=JobKind.THUMBNAIL,
                    resource_id=ResourceId(str(file.id_.value)),
                    at=Timestamp(self._clock.now()),
                )
                if not await self._job_writer.find_by_dedup_key(
                    dedup_key=task.dedup_key
                ):
                    await self._job_writer.add(entity=task)
        for part in parts:
            await self._storage.delete(part.object_key.value)
