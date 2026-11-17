from sqlalchemy import Column, Integer, String, Table

from universal_bot.infrastructure.persistence.sqla.registry import metadata

telegram_update_table = Table(
    "telegram_update",
    metadata,
    Column("id", Integer, primary_key=True, nullable=False),
    Column("payload", String, nullable=False),
    Column("created_at", Integer, nullable=False),
    Column("state", String, nullable=False),
)
