from sqlalchemy import Column, ForeignKey, Integer, String, Table, UniqueConstraint

from universal_bot.infrastructure.persistence.sqla.registry import metadata

verification_table = Table(
    "verification",
    metadata,
    Column("id", String, primary_key=True, nullable=False),
    Column("file_id", String, ForeignKey("file.id"), nullable=False),
    Column("operation_key", String, nullable=False),
    Column("state", String, nullable=False),
    Column("checked_at", Integer, nullable=True),
    Column("observed_sha256", String, nullable=True),
    Column("observed_size", Integer, nullable=True),
    Column("integrity", String, nullable=True),
    Column("error", String, nullable=True),
    UniqueConstraint("file_id", "operation_key"),
)
