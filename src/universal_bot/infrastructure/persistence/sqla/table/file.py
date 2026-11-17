from sqlalchemy import (
    Column,
    ForeignKey,
    Index,
    Integer,
    String,
    Table,
    UniqueConstraint,
)

from universal_bot.infrastructure.persistence.sqla.registry import metadata

file_table = Table(
    "file",
    metadata,
    Column("id", String, primary_key=True, nullable=False),
    Column("owner_id", Integer, ForeignKey("user.id"), nullable=False),
    Column("upload_id", String, ForeignKey("upload.id"), nullable=False),
    Column("object_key", String, nullable=False),
    Column("original_name", String, nullable=False),
    Column("size_bytes", Integer, nullable=False),
    Column("sha256", String, nullable=False),
    Column("storage_date", String, nullable=False),
    Column("storage_timezone", String, nullable=False),
    Column("mime_type", String, nullable=False),
    Column("media_kind", String, nullable=False),
    Column("created_at", Integer, nullable=False),
    Column("checked_at", Integer, nullable=False),
    Column("state", String, nullable=False),
    Column("trashed_at", Integer, nullable=True),
    Column("purge_after", Integer, nullable=True),
    Column("integrity", String, nullable=False),
    Column("thumbnail_key", String, nullable=True),
    Column("thumbnail_state", String, nullable=False),
    UniqueConstraint("upload_id"),
    UniqueConstraint("object_key"),
)
Index(
    "ix_file_catalog",
    file_table.c.owner_id,
    file_table.c.state,
    file_table.c.storage_date,
    file_table.c.created_at,
    file_table.c.id,
)
