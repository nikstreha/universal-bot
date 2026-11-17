from sqlalchemy import Column, Integer, String, Table

from universal_bot.infrastructure.persistence.sqla.registry import metadata

rate_limit_table = Table(
    "rate_limit",
    metadata,
    Column("key", String, primary_key=True, nullable=False),
    Column("window_start", Integer, nullable=False),
    Column("count", Integer, nullable=False),
)
