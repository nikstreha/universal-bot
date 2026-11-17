from sqlalchemy import Column, ForeignKey, Integer, Table

from universal_bot.infrastructure.persistence.sqla.registry import metadata

whitelist_table = Table(
    "whitelist",
    metadata,
    Column("user_id", Integer, ForeignKey("user.id"), primary_key=True, nullable=False),
    Column("added_at", Integer, nullable=False),
    Column("added_by", Integer, nullable=False),
)
