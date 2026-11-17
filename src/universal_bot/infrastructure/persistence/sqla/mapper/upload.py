from sqlalchemy.orm import composite

from universal_bot.domain.entity.upload import Upload
from universal_bot.domain.enum.upload.state import UploadState
from universal_bot.domain.value_object.auth.failure_reason import FailureReason
from universal_bot.domain.value_object.file.archive_date import ArchiveDate
from universal_bot.domain.value_object.file.archive_timezone import ArchiveTimezone
from universal_bot.domain.value_object.file.idempotency_key import IdempotencyKey
from universal_bot.domain.value_object.file.mime_type import MimeType
from universal_bot.domain.value_object.file.name import FileName
from universal_bot.domain.value_object.file.sha256 import SHA256Digest
from universal_bot.domain.value_object.file.size import FileSize
from universal_bot.domain.value_object.stored_file.id import StoredFileId
from universal_bot.domain.value_object.time.timestamp import Timestamp
from universal_bot.domain.value_object.upload.id import UploadId
from universal_bot.domain.value_object.upload.part_size import PartSize
from universal_bot.domain.value_object.user.id import TelegramUserId
from universal_bot.infrastructure.persistence.sqla.registry import mapping_registry
from universal_bot.infrastructure.persistence.sqla.table.upload import upload_table
from universal_bot.infrastructure.persistence.sqla.type import EnumStringType


def map_upload_table() -> None:
    upload_table.c.state.type = EnumStringType(UploadState)
    mapping_registry.map_imperatively(
        Upload,
        upload_table,
        properties={
            "_id": composite(UploadId, upload_table.c.id),
            "owner_id": composite(TelegramUserId, upload_table.c.owner_id),
            "operation_key": composite(IdempotencyKey, upload_table.c.operation_key),
            "original_name": composite(FileName, upload_table.c.original_name),
            "size_bytes": composite(FileSize, upload_table.c.size_bytes),
            "sha256": composite(SHA256Digest, upload_table.c.sha256),
            "declared_mime": composite(MimeType, upload_table.c.declared_mime),
            "storage_date": composite(ArchiveDate, upload_table.c.storage_date),
            "storage_timezone": composite(
                ArchiveTimezone, upload_table.c.storage_timezone
            ),
            "part_bytes": composite(PartSize, upload_table.c.part_bytes),
            "created_at": composite(Timestamp, upload_table.c.created_at),
            "expires_at": composite(Timestamp, upload_table.c.expires_at),
            "_state": upload_table.c.state,
            "file_id": composite(StoredFileId.from_raw, upload_table.c.file_id),
            "error": composite(FailureReason.from_raw, upload_table.c.error),
        },
        column_prefix="_raw_",
    )
