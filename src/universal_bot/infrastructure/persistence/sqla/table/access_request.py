from sqlalchemy import Column, ForeignKey, Integer, String, Table, UniqueConstraint

from universal_bot.infrastructure.persistence.sqla.registry import metadata

access_request_table = Table(
    "access_request",
    metadata,
    Column("id", String, primary_key=True, nullable=False),
    Column("user_id", Integer, ForeignKey("user.id"), nullable=False),
    Column("source", String, nullable=False),
    Column("created_at", Integer, nullable=False),
    Column("status", String, nullable=False),
    Column("decided_at", Integer, nullable=True),
    Column("decided_by", Integer, nullable=True),
    UniqueConstraint("user_id"),
)
