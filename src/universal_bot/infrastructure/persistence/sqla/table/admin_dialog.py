from sqlalchemy import Column, Integer, String, Table

from universal_bot.infrastructure.persistence.sqla.registry import metadata

admin_dialog_table = Table(
    "admin_dialog",
    metadata,
    Column("admin_id", Integer, primary_key=True, nullable=False),
    Column("action", String, nullable=False),
    Column("expires_at", Integer, nullable=False),
    Column("payload", String, nullable=False),
)
