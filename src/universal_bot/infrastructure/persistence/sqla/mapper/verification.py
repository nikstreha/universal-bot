from sqlalchemy.orm import composite

from universal_bot.domain.entity.verification import Verification
from universal_bot.domain.enum.file.integrity import FileIntegrity
from universal_bot.domain.enum.verification.state import VerificationState
from universal_bot.domain.value_object.auth.failure_reason import FailureReason
from universal_bot.domain.value_object.file.idempotency_key import IdempotencyKey
from universal_bot.domain.value_object.file.sha256 import SHA256Digest
from universal_bot.domain.value_object.file.size import FileSize
from universal_bot.domain.value_object.stored_file.id import StoredFileId
from universal_bot.domain.value_object.time.timestamp import Timestamp
from universal_bot.domain.value_object.verification.id import VerificationId
from universal_bot.infrastructure.persistence.sqla.registry import mapping_registry
from universal_bot.infrastructure.persistence.sqla.table.verification import (
    verification_table,
)
from universal_bot.infrastructure.persistence.sqla.type import EnumStringType


def map_verification_table() -> None:
    verification_table.c.state.type = EnumStringType(VerificationState)
    verification_table.c.integrity.type = EnumStringType(FileIntegrity)
    mapping_registry.map_imperatively(
        Verification,
        verification_table,
        properties={
            "_id": composite(VerificationId, verification_table.c.id),
            "file_id": composite(StoredFileId, verification_table.c.file_id),
            "operation_key": composite(
                IdempotencyKey, verification_table.c.operation_key
            ),
            "_state": verification_table.c.state,
            "checked_at": composite(
                Timestamp.from_raw, verification_table.c.checked_at
            ),
            "observed_sha256": composite(
                SHA256Digest.from_raw, verification_table.c.observed_sha256
            ),
            "observed_size": composite(
                FileSize.from_raw, verification_table.c.observed_size
            ),
            "integrity": verification_table.c.integrity,
            "error": composite(FailureReason.from_raw, verification_table.c.error),
        },
        column_prefix="_raw_",
    )
