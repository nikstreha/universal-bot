from sqlalchemy import Column, ForeignKey, Integer, String, Table, UniqueConstraint

from universal_bot.infrastructure.persistence.sqla.registry import metadata

session_table = Table(
    "session",
    metadata,
    Column("id", String, primary_key=True, nullable=False),
    Column("user_id", Integer, ForeignKey("user.id"), nullable=False),
    Column("token_hash", String, nullable=False),
    Column("installation_id", String, nullable=False),
    Column("device_name", String, nullable=False),
    Column("created_at", Integer, nullable=False),
    Column("last_seen_at", Integer, nullable=False),
    Column("expires_at", Integer, nullable=False),
    Column("absolute_expires_at", Integer, nullable=False),
    Column("revoked_at", Integer, nullable=True),
    UniqueConstraint("token_hash"),
)
