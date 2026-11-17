from sqlalchemy.orm import composite

from universal_bot.domain.entity.upload_part import UploadPart
from universal_bot.domain.value_object.file.object_key import ObjectKey
from universal_bot.domain.value_object.file.sha256 import SHA256Digest
from universal_bot.domain.value_object.file.size import FileSize
from universal_bot.domain.value_object.upload.part_id import UploadPartId
from universal_bot.infrastructure.persistence.sqla.registry import mapping_registry
from universal_bot.infrastructure.persistence.sqla.table.upload_part import (
    upload_part_table,
)


def map_upload_part_table() -> None:
    mapping_registry.map_imperatively(
        UploadPart,
        upload_part_table,
        properties={
            "_id": composite(
                UploadPartId,
                upload_part_table.c.upload_id,
                upload_part_table.c.part_index,
            ),
            "size_bytes": composite(FileSize, upload_part_table.c.size_bytes),
            "sha256": composite(SHA256Digest, upload_part_table.c.sha256),
            "object_key": composite(ObjectKey, upload_part_table.c.object_key),
        },
        column_prefix="_raw_",
    )
