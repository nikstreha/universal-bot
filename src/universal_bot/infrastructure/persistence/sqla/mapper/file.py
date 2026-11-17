from sqlalchemy.orm import composite

from universal_bot.domain.entity.stored_file import StoredFile
from universal_bot.domain.enum.file.integrity import FileIntegrity
from universal_bot.domain.enum.file.media_kind import MediaKind
from universal_bot.domain.enum.file.state import FileState
from universal_bot.domain.enum.file.thumbnail_state import ThumbnailState
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
from universal_bot.infrastructure.persistence.sqla.registry import mapping_registry
from universal_bot.infrastructure.persistence.sqla.table.file import file_table
from universal_bot.infrastructure.persistence.sqla.type import EnumStringType


def map_file_table() -> None:
    file_table.c.media_kind.type = EnumStringType(MediaKind)
    file_table.c.state.type = EnumStringType(FileState)
    file_table.c.integrity.type = EnumStringType(FileIntegrity)
    file_table.c.thumbnail_state.type = EnumStringType(ThumbnailState)
    mapping_registry.map_imperatively(
        StoredFile,
        file_table,
        properties={
            "_id": composite(StoredFileId, file_table.c.id),
            "owner_id": composite(TelegramUserId, file_table.c.owner_id),
            "upload_id": composite(UploadId, file_table.c.upload_id),
            "object_key": composite(ObjectKey, file_table.c.object_key),
            "original_name": composite(FileName, file_table.c.original_name),
            "size_bytes": composite(FileSize, file_table.c.size_bytes),
            "sha256": composite(SHA256Digest, file_table.c.sha256),
            "storage_date": composite(ArchiveDate, file_table.c.storage_date),
            "storage_timezone": composite(
                ArchiveTimezone, file_table.c.storage_timezone
            ),
            "mime_type": composite(MimeType, file_table.c.mime_type),
            "media_kind": file_table.c.media_kind,
            "created_at": composite(Timestamp, file_table.c.created_at),
            "checked_at": composite(Timestamp, file_table.c.checked_at),
            "_state": file_table.c.state,
            "trashed_at": composite(Timestamp.from_raw, file_table.c.trashed_at),
            "purge_after": composite(Timestamp.from_raw, file_table.c.purge_after),
            "integrity": file_table.c.integrity,
            "thumbnail_key": composite(ObjectKey.from_raw, file_table.c.thumbnail_key),
            "thumbnail_state": file_table.c.thumbnail_state,
        },
        column_prefix="_raw_",
    )
