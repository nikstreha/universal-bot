from sqlalchemy import Column, Integer, String, Table, UniqueConstraint

from universal_bot.infrastructure.persistence.sqla.registry import metadata

delivery_table = Table(
    "delivery",
    metadata,
    Column("id", String, primary_key=True, nullable=False),
    Column("dedup_key", String, nullable=False),
    Column("chat_id", Integer, nullable=False),
    Column("text", String, nullable=False),
    Column("next_attempt_at", Integer, nullable=False),
    Column("created_at", Integer, nullable=False),
    Column("reply_to", Integer, nullable=True),
    Column("filename", String, nullable=True),
    Column("user_id", Integer, nullable=True),
    Column("state", String, nullable=False),
    Column("lease_until", Integer, nullable=True),
    Column("message_id", Integer, nullable=True),
    UniqueConstraint("dedup_key"),
)
