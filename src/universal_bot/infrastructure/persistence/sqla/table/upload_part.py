from sqlalchemy import Column, ForeignKey, Integer, String, Table

from universal_bot.infrastructure.persistence.sqla.registry import metadata

upload_part_table = Table(
    "upload_part",
    metadata,
    Column(
        "upload_id", String, ForeignKey("upload.id"), primary_key=True, nullable=False
    ),
    Column("part_index", Integer, primary_key=True, nullable=False),
    Column("size_bytes", Integer, nullable=False),
    Column("sha256", String, nullable=False),
    Column("object_key", String, nullable=False),
)
