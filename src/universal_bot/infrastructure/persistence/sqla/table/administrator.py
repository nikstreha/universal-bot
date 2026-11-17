from sqlalchemy import (
    CheckConstraint,
    Column,
    ForeignKey,
    Integer,
    Table,
    UniqueConstraint,
)

from universal_bot.infrastructure.persistence.sqla.registry import metadata

administrator_table = Table(
    "administrator",
    metadata,
    Column("id", Integer, primary_key=True, nullable=False),
    Column("user_id", Integer, ForeignKey("user.id"), nullable=False),
    Column("created_at", Integer, nullable=False),
    CheckConstraint("id = 1", name="ck_administrator_singleton"),
    CheckConstraint("user_id > 0", name="ck_administrator_user_id_positive"),
    UniqueConstraint("user_id"),
)
