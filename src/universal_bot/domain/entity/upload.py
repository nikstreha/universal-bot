from universal_bot.domain.entity.common import Entity
from universal_bot.domain.entity.upload_part import UploadPart
from universal_bot.domain.enum.upload.state import UploadState
from universal_bot.domain.exception.common import (
    InvalidMetadataError,
    InvalidRangeError,
    NotFoundError,
)
from universal_bot.domain.exception.upload import (
    UploadAlreadyCompletedError,
    UploadExpiredError,
    UploadInvalidStateError,
    UploadPartsMissingError,
    UploadStoppedError,
)
from universal_bot.domain.value_object.auth.failure_reason import FailureReason
from universal_bot.domain.value_object.file.archive_date import ArchiveDate
from universal_bot.domain.value_object.file.archive_timezone import ArchiveTimezone
from universal_bot.domain.value_object.file.idempotency_key import IdempotencyKey
from universal_bot.domain.value_object.file.mime_type import MimeType
from universal_bot.domain.value_object.file.name import FileName
from universal_bot.domain.value_object.file.object_key import ObjectKey
from universal_bot.domain.value_object.file.sha256 import SHA256Digest
from universal_bot.domain.value_object.file.size import FileSize
from universal_bot.domain.value_object.stored_file.id import StoredFileId
from universal_bot.domain.value_object.time.timestamp import Timestamp
from universal_bot.domain.value_object.upload.id import UploadId
from universal_bot.domain.value_object.upload.part_index import PartIndex
from universal_bot.domain.value_object.upload.part_size import PartSize
from universal_bot.domain.value_object.user.id import TelegramUserId


class Upload(Entity[UploadId]):
    _id: UploadId
    owner_id: TelegramUserId
    operation_key: IdempotencyKey
    original_name: FileName
    size_bytes: FileSize
    sha256: SHA256Digest
    declared_mime: MimeType
    storage_date: ArchiveDate
    storage_timezone: ArchiveTimezone
    part_bytes: PartSize
    created_at: Timestamp
    expires_at: Timestamp
    state: UploadState
    file_id: StoredFileId | None
    error: FailureReason | None

    def __init__(
        self,
        *,
        id_: UploadId,
        owner_id: TelegramUserId,
        operation_key: IdempotencyKey,
        original_name: FileName,
        size_bytes: FileSize,
        sha256: SHA256Digest,
        declared_mime: MimeType,
        storage_date: ArchiveDate,
        storage_timezone: ArchiveTimezone,
        part_bytes: PartSize,
        created_at: Timestamp,
        expires_at: Timestamp,
        state: UploadState = UploadState.RECEIVING,
        file_id: StoredFileId | None = None,
        error: FailureReason | None = None,
    ) -> None:
        super().__init__(id_=id_)
        self.owner_id = owner_id
        self.operation_key = operation_key
        self.original_name = original_name
        self.size_bytes = size_bytes
        self.sha256 = sha256
        self.declared_mime = declared_mime
        self.storage_date = storage_date
        self.storage_timezone = storage_timezone
        self.part_bytes = part_bytes
        self.created_at = created_at
        self.expires_at = expires_at
        self._state = state
        self.file_id = file_id
        self.error = error

    @property
    def state(self) -> UploadState:
        return self._state

    def require_owner(self, user_id: TelegramUserId) -> None:
        if self.owner_id != user_id:
            raise NotFoundError("Загрузка не найдена")

    def accept(self, at: Timestamp) -> None:
        if self.state is not UploadState.RECEIVING:
            raise UploadInvalidStateError()
        if self.expires_at.value <= at.value:
            raise UploadExpiredError()

    def expected_part_size(self, index: PartIndex, at: Timestamp) -> FileSize:
        self.accept(at)
        if index.value >= self.part_count:
            raise InvalidRangeError("Неверный номер части")
        return FileSize(
            min(
                self.part_bytes.value,
                self.size_bytes.value - index.value * self.part_bytes.value,
            )
        )

    def record_part(self, part: UploadPart, at: Timestamp, idle_seconds: int) -> None:
        expected = self.expected_part_size(part.part_index, at)
        if part.upload_id != self.id_ or part.size_bytes != expected:
            raise InvalidRangeError(
                "Часть не принадлежит загрузке или имеет неверный размер"
            )
        self.expires_at = at.after(idle_seconds)

    def verify(self, count: int, size: FileSize, at: Timestamp) -> bool:
        if self.state in (UploadState.VERIFYING, UploadState.COMPLETED):
            return False
        self.accept(at)
        if count != self.part_count or size != self.size_bytes:
            raise UploadPartsMissingError()
        self._state = UploadState.VERIFYING
        return True

    def matches(
        self, name: FileName, size: FileSize, digest: SHA256Digest, mime: MimeType
    ) -> bool:
        return (
            self.original_name,
            self.size_bytes,
            self.sha256,
            self.declared_mime,
        ) == (name, size, digest, mime)

    def cancel(self) -> None:
        if self.state is UploadState.COMPLETED:
            raise UploadAlreadyCompletedError(
                file_id=str(self.file_id.value) if self.file_id else None
            )
        self._state = UploadState.CANCELLED

    def expire(self, at: Timestamp) -> bool:
        if self.state is UploadState.RECEIVING and self.expires_at.value <= at.value:
            self._state = UploadState.EXPIRED
            return True
        return False

    def fail(self, reason: FailureReason) -> None:
        if self.state is UploadState.VERIFYING:
            self._state = UploadState.FAILED
            self.error = reason

    def complete(self, file_id: StoredFileId) -> None:
        if self.state is not UploadState.VERIFYING:
            raise UploadStoppedError()
        self.file_id = file_id
        self._state = UploadState.COMPLETED

    def original_key(self, generation: int) -> ObjectKey:
        if generation <= 0:
            raise InvalidMetadataError("Неверное поколение задачи")
        date = self.storage_date.value.strftime("%Y/%m/%d")
        return ObjectKey(
            f"owners/{self.owner_id.value}/{date}/uploads/{self.id_.value}/{generation}/original"
        )

    @property
    def part_count(self) -> int:
        return (
            self.size_bytes.value + self.part_bytes.value - 1
        ) // self.part_bytes.value
