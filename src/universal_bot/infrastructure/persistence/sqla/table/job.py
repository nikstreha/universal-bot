from sqlalchemy import Column, Index, Integer, String, Table, UniqueConstraint

from universal_bot.infrastructure.persistence.sqla.registry import metadata

job_table = Table(
    "job",
    metadata,
    Column("id", String, primary_key=True, nullable=False),
    Column("kind", String, nullable=False),
    Column("resource_id", String, nullable=False),
    Column("dedup_key", String, nullable=False),
    Column("next_attempt_at", Integer, nullable=False),
    Column("created_at", Integer, nullable=False),
    Column("state", String, nullable=False),
    Column("lease_until", Integer, nullable=True),
    Column("generation", Integer, nullable=False),
    Column("attempts", Integer, nullable=False),
    Column("error", String, nullable=True),
    UniqueConstraint("dedup_key"),
)
Index("ix_job_queue", job_table.c.kind, job_table.c.state, job_table.c.next_attempt_at)
