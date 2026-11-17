from sqlalchemy import Column, ForeignKey, Integer, String, Table, UniqueConstraint

from universal_bot.infrastructure.persistence.sqla.registry import metadata

upload_table = Table(
    "upload",
    metadata,
    Column("id", String, primary_key=True, nullable=False),
    Column("owner_id", Integer, ForeignKey("user.id"), nullable=False),
    Column("operation_key", String, nullable=False),
    Column("original_name", String, nullable=False),
    Column("size_bytes", Integer, nullable=False),
    Column("sha256", String, nullable=False),
    Column("declared_mime", String, nullable=False),
    Column("storage_date", String, nullable=False),
    Column("storage_timezone", String, nullable=False),
    Column("part_bytes", Integer, nullable=False),
    Column("created_at", Integer, nullable=False),
    Column("expires_at", Integer, nullable=False),
    Column("state", String, nullable=False),
    Column("file_id", String, nullable=True),
    Column("error", String, nullable=True),
    UniqueConstraint("owner_id", "operation_key"),
)
