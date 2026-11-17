from sqlalchemy import Column, Integer, String, Table

from universal_bot.infrastructure.persistence.sqla.registry import metadata

audit_event_table = Table(
    "audit_event",
    metadata,
    Column("id", String, primary_key=True, nullable=False),
    Column("actor_id", Integer, nullable=False),
    Column("target_id", Integer, nullable=False),
    Column("action", String, nullable=False),
    Column("created_at", Integer, nullable=False),
)
