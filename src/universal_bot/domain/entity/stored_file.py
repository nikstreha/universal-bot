from universal_bot.domain.entity.common import Entity
from universal_bot.domain.entity.upload import Upload
from universal_bot.domain.enum.file.integrity import FileIntegrity
from universal_bot.domain.enum.file.media_kind import MediaKind
from universal_bot.domain.enum.file.state import FileState
from universal_bot.domain.enum.file.thumbnail_state import ThumbnailState
from universal_bot.domain.enum.upload.state import UploadState
from universal_bot.domain.exception.common import NotFoundError
from universal_bot.domain.exception.file import ChecksumMismatchError, FileTrashedError
from universal_bot.domain.exception.stored_file import (
    StoredFileInvalidStateError,
    StoredFileRestoreExpiredError,
)
from universal_bot.domain.value_object.file.archive_date import ArchiveDate
from universal_bot.domain.value_object.file.archive_timezone import ArchiveTimezone
from universal_bot.domain.value_object.file.mime_type import MimeType
from universal_bot.domain.value_object.file.name import FileName
from universal_bot.domain.value_object.file.object_key import ObjectKey
from universal_bot.domain.value_object.file.sha256 import SHA256Digest
from universal_bot.domain.value_object.file.size import FileSize
from universal_bot.domain.value_object.stored_file.id import StoredFileId
from universal_bot.domain.value_object.time.timestamp import Timestamp
from universal_bot.domain.value_object.upload.id import UploadId
from universal_bot.domain.value_object.user.id import TelegramUserId


class StoredFile(Entity[StoredFileId]):
    _id: StoredFileId
    owner_id: TelegramUserId
    upload_id: UploadId
    object_key: ObjectKey
    original_name: FileName
    size_bytes: FileSize
    sha256: SHA256Digest
    storage_date: ArchiveDate
    storage_timezone: ArchiveTimezone
    mime_type: MimeType
    media_kind: MediaKind
    created_at: Timestamp
    checked_at: Timestamp
    state: FileState
    trashed_at: Timestamp | None
    purge_after: Timestamp | None
    integrity: FileIntegrity
    thumbnail_key: ObjectKey | None
    thumbnail_state: ThumbnailState

    def __init__(
        self,
        *,
        id_: StoredFileId,
        owner_id: TelegramUserId,
        upload_id: UploadId,
        object_key: ObjectKey,
        original_name: FileName,
        size_bytes: FileSize,
        sha256: SHA256Digest,
        storage_date: ArchiveDate,
        storage_timezone: ArchiveTimezone,
        mime_type: MimeType,
        media_kind: MediaKind,
        created_at: Timestamp,
        checked_at: Timestamp,
        state: FileState = FileState.ACTIVE,
        trashed_at: Timestamp | None = None,
        purge_after: Timestamp | None = None,
        integrity: FileIntegrity = FileIntegrity.VERIFIED,
        thumbnail_key: ObjectKey | None = None,
        thumbnail_state: ThumbnailState = ThumbnailState.PENDING,
    ) -> None:
        super().__init__(id_=id_)
        self.owner_id = owner_id
        self.upload_id = upload_id
        self.object_key = object_key
        self.original_name = original_name
        self.size_bytes = size_bytes
        self.sha256 = sha256
        self.storage_date = storage_date
        self.storage_timezone = storage_timezone
        self.mime_type = mime_type
        self.media_kind = media_kind
        self.created_at = created_at
        self.checked_at = checked_at
        self._state = state
        self.trashed_at = trashed_at
        self.purge_after = purge_after
        self.integrity = integrity
        self.thumbnail_key = thumbnail_key
        self.thumbnail_state = thumbnail_state

    @classmethod
    def from_upload(
        cls,
        *,
        id_: StoredFileId,
        upload: Upload,
        object_key: ObjectKey,
        observed_size: FileSize,
        observed_digest: SHA256Digest,
        mime: MimeType,
        media_kind: MediaKind,
        at: Timestamp,
    ) -> StoredFile:
        if upload.state is not UploadState.VERIFYING:
            raise StoredFileInvalidStateError()
        if (observed_size, observed_digest) != (upload.size_bytes, upload.sha256):
            raise ChecksumMismatchError("Сохранённый файл не прошёл проверку")
        return cls(
            id_=id_,
            owner_id=upload.owner_id,
            upload_id=upload.id_,
            object_key=object_key,
            original_name=upload.original_name,
            size_bytes=observed_size,
            sha256=observed_digest,
            storage_date=upload.storage_date,
            storage_timezone=upload.storage_timezone,
            mime_type=mime,
            media_kind=media_kind,
            created_at=at,
            checked_at=at,
            thumbnail_state=(
                ThumbnailState.PENDING
                if media_kind in (MediaKind.PHOTO, MediaKind.VIDEO)
                else ThumbnailState.UNSUPPORTED
            ),
        )

    @property
    def state(self) -> FileState:
        return self._state

    def require_owner(self, user_id: TelegramUserId) -> None:
        if self.owner_id != user_id or self.state is FileState.PURGING:
            raise NotFoundError("Файл не найден")

    def require_active(self) -> None:
        if self.state is not FileState.ACTIVE:
            raise FileTrashedError("Сначала восстановите файл")

    def trash(self, at: Timestamp, retention: int) -> None:
        if self.state is FileState.TRASHED:
            return
        if self.state is not FileState.ACTIVE or retention < 0:
            raise StoredFileInvalidStateError()
        self.trashed_at, self.purge_after = (at, at.after(retention))
        self._state = FileState.TRASHED

    def restore(self, at: Timestamp) -> None:
        if self.state is FileState.ACTIVE:
            return
        if (
            self.state is not FileState.TRASHED
            or self.purge_after is None
            or self.purge_after.value <= at.value
        ):
            raise StoredFileRestoreExpiredError()
        self.trashed_at = self.purge_after = None
        self._state = FileState.ACTIVE

    def begin_purge(self, at: Timestamp) -> bool:
        if self.state is FileState.PURGING:
            return True
        if (
            self.state is not FileState.TRASHED
            or self.purge_after is None
            or self.purge_after.value > at.value
        ):
            return False
        self._state = FileState.PURGING
        return True

    def record_integrity(
        self, digest: SHA256Digest, size: FileSize, at: Timestamp
    ) -> FileIntegrity:
        self.require_active()
        self.integrity = (
            FileIntegrity.VERIFIED
            if (self.sha256, self.size_bytes) == (digest, size)
            else FileIntegrity.CORRUPT
        )
        self.checked_at = at
        return self.integrity

    def thumbnail_target(self, generation: int) -> ObjectKey:
        self.require_active()
        date = self.storage_date.value.strftime("%Y/%m/%d")
        return ObjectKey(
            f"owners/{self.owner_id.value}/{date}/files/{self.id_.value}/thumbnail-{generation}.jpg"
        )

    def publish_thumbnail(self, key: ObjectKey) -> None:
        self.require_active()
        self.thumbnail_key, self.thumbnail_state = (key, ThumbnailState.READY)

    def thumbnail_failed(self) -> None:
        if self.thumbnail_state is not ThumbnailState.READY:
            self.thumbnail_state = ThumbnailState.FAILED
