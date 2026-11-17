from sqlalchemy import Column, Integer, String, Table

from universal_bot.infrastructure.persistence.sqla.registry import metadata

user_table = Table(
    "user",
    metadata,
    Column("id", Integer, primary_key=True, nullable=False),
    Column("name", String, nullable=False),
    Column("created_at", Integer, nullable=False),
    Column("last_seen_at", Integer, nullable=False),
)
