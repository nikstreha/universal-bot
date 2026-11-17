from sqlalchemy import Column, String, Table

from universal_bot.infrastructure.persistence.sqla.registry import metadata

service_state_table = Table(
    "service_state",
    metadata,
    Column("key", String, primary_key=True, nullable=False),
    Column("value", String, nullable=False),
)
