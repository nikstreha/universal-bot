from sqlalchemy import Column, ForeignKey, Integer, String, Table

from universal_bot.infrastructure.persistence.sqla.registry import metadata

auth_attempt_table = Table(
    "auth_attempt",
    metadata,
    Column("id", String, primary_key=True, nullable=False),
    Column("challenge", String, nullable=False),
    Column("login_code", String, nullable=False),
    Column("installation_id", String, nullable=False),
    Column("device_name", String, nullable=False),
    Column("expires_at", Integer, nullable=False),
    Column("status", String, nullable=False),
    Column("candidate_id", Integer, ForeignKey("user.id"), nullable=True),
    Column("user_id", Integer, ForeignKey("user.id"), nullable=True),
    Column("consumed_at", Integer, nullable=True),
)
