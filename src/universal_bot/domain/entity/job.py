from universal_bot.domain.entity.common import Entity
from universal_bot.domain.enum.job.kind import JobKind
from universal_bot.domain.enum.job.state import JobState
from universal_bot.domain.exception.job import (
    JobAlreadyClaimedError,
    JobInvalidStateError,
    JobLeaseLostError,
)
from universal_bot.domain.value_object.auth.failure_reason import FailureReason
from universal_bot.domain.value_object.job.deduplication_key import DeduplicationKey
from universal_bot.domain.value_object.job.id import JobId
from universal_bot.domain.value_object.job.resource_id import ResourceId
from universal_bot.domain.value_object.time.timestamp import Timestamp


class Job(Entity[JobId]):
    _id: JobId
    kind: JobKind
    resource_id: ResourceId
    dedup_key: DeduplicationKey
    next_attempt_at: Timestamp
    created_at: Timestamp
    state: JobState
    lease_until: Timestamp | None
    generation: int
    attempts: int
    error: FailureReason | None

    def __init__(
        self,
        *,
        id_: JobId,
        kind: JobKind,
        resource_id: ResourceId,
        dedup_key: DeduplicationKey,
        next_attempt_at: Timestamp,
        created_at: Timestamp,
        state: JobState = JobState.QUEUED,
        lease_until: Timestamp | None = None,
        generation: int = 0,
        attempts: int = 0,
        error: FailureReason | None = None,
    ) -> None:
        super().__init__(id_=id_)
        self.kind = kind
        self.resource_id = resource_id
        self.dedup_key = dedup_key
        self.next_attempt_at = next_attempt_at
        self.created_at = created_at
        self._state = state
        self.lease_until = lease_until
        self.generation = generation
        self.attempts = attempts
        self.error = error

    @property
    def state(self) -> JobState:
        return self._state

    @classmethod
    def create(
        cls, *, id_: JobId, kind: JobKind, resource_id: ResourceId, at: Timestamp
    ) -> Job:
        return cls(
            id_=id_,
            kind=kind,
            resource_id=resource_id,
            dedup_key=DeduplicationKey(f"{kind.value}:{resource_id.value}"),
            next_attempt_at=at,
            created_at=at,
        )

    def claim(self, at: Timestamp) -> None:
        queued = self.state is JobState.QUEUED
        abandoned = (
            self.state is JobState.RUNNING
            and self.lease_until is not None
            and (self.lease_until.value <= at.value)
        )
        if self.next_attempt_at.value > at.value or not (queued or abandoned):
            raise JobAlreadyClaimedError()
        self._state = JobState.RUNNING
        self.lease_until = at.after(120)
        self.generation += 1
        self.attempts += 1

    def validate_lease(self, generation: int, at: Timestamp) -> None:
        if (
            self.state is not JobState.RUNNING
            or self.generation != generation
            or self.lease_until is None
            or (self.lease_until.value <= at.value)
        ):
            raise JobLeaseLostError()

    def renew(self, generation: int, at: Timestamp) -> None:
        self.validate_lease(generation, at)
        self.lease_until = at.after(120)

    def fail(self, reason: FailureReason, at: Timestamp) -> bool:
        if self.state is not JobState.RUNNING:
            raise JobInvalidStateError()
        self.error = reason
        terminal = self.attempts >= 3 or reason.value == "CHECKSUM_MISMATCH"
        self._state = JobState.FAILED if terminal else JobState.QUEUED
        self.next_attempt_at = at.after(min(300, 10 * 2**self.attempts))
        return terminal

    def succeed(self) -> None:
        if self.state is not JobState.RUNNING:
            raise JobInvalidStateError()
        self._state = JobState.COMPLETED
