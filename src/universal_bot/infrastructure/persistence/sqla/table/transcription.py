from sqlalchemy import Column, ForeignKey, Integer, String, Table, UniqueConstraint

from universal_bot.infrastructure.persistence.sqla.registry import metadata

transcription_table = Table(
    "transcription",
    metadata,
    Column("id", String, primary_key=True, nullable=False),
    Column("owner_id", Integer, ForeignKey("user.id"), nullable=False),
    Column("chat_id", Integer, nullable=False),
    Column("message_id", Integer, nullable=False),
    Column("telegram_file_id", String, nullable=False),
    Column("created_at", Integer, nullable=False),
    Column("state", String, nullable=False),
    Column("text", String, nullable=True),
    Column("error", String, nullable=True),
    Column("response_message_id", Integer, nullable=True),
    Column("finished_at", Integer, nullable=True),
    UniqueConstraint("chat_id", "message_id"),
)
