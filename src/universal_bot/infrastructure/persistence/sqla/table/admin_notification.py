from sqlalchemy import Column, ForeignKey, Integer, String, Table, UniqueConstraint

from universal_bot.infrastructure.persistence.sqla.registry import metadata

admin_notification_table = Table(
    "admin_notification",
    metadata,
    Column("id", String, primary_key=True, nullable=False),
    Column("event_key", String, nullable=False),
    Column("user_id", Integer, ForeignKey("user.id"), nullable=False),
    Column("source", String, nullable=False),
    Column("outcome", String, nullable=False),
    Column("created_at", Integer, nullable=False),
    Column("read_at", Integer, nullable=True),
    UniqueConstraint("event_key"),
)
