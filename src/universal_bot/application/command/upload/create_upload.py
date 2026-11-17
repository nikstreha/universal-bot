import asyncio

from universal_bot.application.dto.common.policy import Policy
from universal_bot.application.dto.upload.create_upload import CreateUploadRequestDTO
from universal_bot.application.exception.common import (
    FileTooLargeError,
    IdempotencyConflictError,
    LimitReachedError,
)
from universal_bot.application.port.clock import IClock
from universal_bot.application.port.persistence.file_storage.object_storage import (
    IObjectStorage,
)
from universal_bot.application.port.persistence.repository.upload.writer import (
    IUploadWriter,
)
from universal_bot.application.port.persistence.uow import IUnitOfWork
from universal_bot.application.port.security.secrets import ISecrets
from universal_bot.application.service.access.access_policy import AccessPolicy
from universal_bot.domain.common.guard import ensure
from universal_bot.domain.entity.upload import Upload
from universal_bot.domain.enum.upload.state import UploadState
from universal_bot.domain.value_object.file.archive_date import ArchiveDate
from universal_bot.domain.value_object.file.archive_timezone import ArchiveTimezone
from universal_bot.domain.value_object.file.idempotency_key import IdempotencyKey
from universal_bot.domain.value_object.file.mime_type import MimeType
from universal_bot.domain.value_object.file.name import FileName
from universal_bot.domain.value_object.file.sha256 import SHA256Digest
from universal_bot.domain.value_object.file.size import FileSize
from universal_bot.domain.value_object.time.timestamp import Timestamp
from universal_bot.domain.value_object.upload.id import UploadId
from universal_bot.domain.value_object.upload.part_size import PartSize
from universal_bot.domain.value_object.user.id import TelegramUserId


class CreateUploadInteractor:
    def __init__(
        self,
        *,
        access_policy: AccessPolicy,
        clock: IClock,
        policy: Policy,
        secrets: ISecrets,
        storage: IObjectStorage,
        uow: IUnitOfWork,
        upload_writer: IUploadWriter,
    ) -> None:
        self._access_policy = access_policy
        self._clock = clock
        self._policy = policy
        self._secrets = secrets
        self._storage = storage
        self._uow = uow
        self._upload_writer = upload_writer

    async def __call__(self, *, request: CreateUploadRequestDTO) -> tuple[str, bool]:
        owner_id = TelegramUserId(request.user_id)
        operation_key = IdempotencyKey(request.operation_key)
        original_name = FileName(request.original_name)
        size = FileSize(request.size_bytes)
        digest = SHA256Digest(request.sha256)
        mime = MimeType(request.declared_mime)
        ensure(
            size.value <= self._policy.max_file_bytes,
            FileTooLargeError,
            "Размер файла превышает лимит",
        )
        await asyncio.to_thread(self._storage.ready)
        async with self._uow:
            await self._access_policy.require_access(user_id=owner_id.value)
            existing = await self._upload_writer.find_by_owner_id_and_operation_key(
                owner_id=owner_id,
                operation_key=operation_key,
            )
            if existing:
                ensure(
                    existing.matches(original_name, size, digest, mime),
                    IdempotencyConflictError,
                    "Ключ уже использован для другого файла",
                )
                return (str(existing.id_.value), False)
            active = await self._upload_writer.list_by_states_expiring_after(
                states=(UploadState.RECEIVING, UploadState.VERIFYING),
                expires_after=Timestamp(self._clock.now()),
            )
            ensure(
                sum(row.owner_id == owner_id for row in active)
                < self._policy.max_open_uploads,
                LimitReachedError,
                "Слишком много незавершённых загрузок",
            )
            await asyncio.to_thread(
                self._storage.guard,
                2 * (size.value + sum(row.size_bytes.value for row in active)),
            )
            row = Upload(
                id_=UploadId(self._secrets.identity()),
                owner_id=owner_id,
                operation_key=operation_key,
                original_name=original_name,
                size_bytes=size,
                sha256=digest,
                declared_mime=mime,
                storage_date=ArchiveDate(
                    self._clock.archive_date(self._policy.archive_timezone)
                ),
                storage_timezone=ArchiveTimezone(self._policy.archive_timezone),
                part_bytes=PartSize(self._policy.part_bytes),
                created_at=Timestamp(self._clock.now()),
                expires_at=Timestamp(
                    self._clock.now() + self._policy.upload_idle_seconds
                ),
            )
            await self._upload_writer.add(entity=row)
            return (str(row.id_.value), True)
