from sqlalchemy.orm import composite

from universal_bot.domain.entity.job import Job
from universal_bot.domain.enum.job.kind import JobKind
from universal_bot.domain.enum.job.state import JobState
from universal_bot.domain.value_object.auth.failure_reason import FailureReason
from universal_bot.domain.value_object.job.deduplication_key import DeduplicationKey
from universal_bot.domain.value_object.job.id import JobId
from universal_bot.domain.value_object.job.resource_id import ResourceId
from universal_bot.domain.value_object.time.timestamp import Timestamp
from universal_bot.infrastructure.persistence.sqla.registry import mapping_registry
from universal_bot.infrastructure.persistence.sqla.table.job import job_table
from universal_bot.infrastructure.persistence.sqla.type import EnumStringType


def map_job_table() -> None:
    job_table.c.kind.type = EnumStringType(JobKind)
    job_table.c.state.type = EnumStringType(JobState)
    mapping_registry.map_imperatively(
        Job,
        job_table,
        properties={
            "_id": composite(JobId, job_table.c.id),
            "kind": job_table.c.kind,
            "resource_id": composite(ResourceId, job_table.c.resource_id),
            "dedup_key": composite(DeduplicationKey, job_table.c.dedup_key),
            "next_attempt_at": composite(Timestamp, job_table.c.next_attempt_at),
            "created_at": composite(Timestamp, job_table.c.created_at),
            "_state": job_table.c.state,
            "lease_until": composite(Timestamp.from_raw, job_table.c.lease_until),
            "generation": job_table.c.generation,
            "attempts": job_table.c.attempts,
            "error": composite(FailureReason.from_raw, job_table.c.error),
        },
        column_prefix="_raw_",
    )
