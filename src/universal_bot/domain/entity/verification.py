from universal_bot.domain.entity.common import Entity
from universal_bot.domain.enum.file.integrity import FileIntegrity
from universal_bot.domain.enum.verification.state import VerificationState
from universal_bot.domain.exception.common import InvalidStateError
from universal_bot.domain.value_object.auth.failure_reason import FailureReason
from universal_bot.domain.value_object.file.idempotency_key import IdempotencyKey
from universal_bot.domain.value_object.file.sha256 import SHA256Digest
from universal_bot.domain.value_object.file.size import FileSize
from universal_bot.domain.value_object.stored_file.id import StoredFileId
from universal_bot.domain.value_object.time.timestamp import Timestamp
from universal_bot.domain.value_object.verification.id import VerificationId


class Verification(Entity[VerificationId]):
    _id: VerificationId
    file_id: StoredFileId
    operation_key: IdempotencyKey
    state: VerificationState
    checked_at: Timestamp | None
    observed_sha256: SHA256Digest | None
    observed_size: FileSize | None
    integrity: FileIntegrity | None
    error: FailureReason | None

    def __init__(
        self,
        *,
        id_: VerificationId,
        file_id: StoredFileId,
        operation_key: IdempotencyKey,
        state: VerificationState = VerificationState.QUEUED,
        checked_at: Timestamp | None = None,
        observed_sha256: SHA256Digest | None = None,
        observed_size: FileSize | None = None,
        integrity: FileIntegrity | None = None,
        error: FailureReason | None = None,
    ) -> None:
        super().__init__(id_=id_)
        self.file_id = file_id
        self.operation_key = operation_key
        self._state = state
        self.checked_at = checked_at
        self.observed_sha256 = observed_sha256
        self.observed_size = observed_size
        self.integrity = integrity
        self.error = error

    @property
    def state(self) -> VerificationState:
        return self._state

    def start(self) -> bool:
        if self.state in (VerificationState.SUCCEEDED, VerificationState.FAILED):
            return False
        self._state = VerificationState.RUNNING
        return True

    def fail(self, reason: FailureReason, at: Timestamp) -> None:
        if self.state is VerificationState.SUCCEEDED:
            return
        self._state = VerificationState.FAILED
        self.error, self.integrity, self.checked_at = (
            reason,
            FileIntegrity.UNAVAILABLE,
            at,
        )

    def record_result(
        self,
        digest: SHA256Digest,
        size: FileSize,
        integrity: FileIntegrity,
        at: Timestamp,
    ) -> None:
        if self.state is not VerificationState.RUNNING:
            raise InvalidStateError("Проверка не выполняется")
        self.observed_sha256, self.observed_size = (digest, size)
        self.integrity, self.checked_at = (integrity, at)
        self._state = (
            VerificationState.SUCCEEDED
            if integrity is FileIntegrity.VERIFIED
            else VerificationState.FAILED
        )
