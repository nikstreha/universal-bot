from sqlalchemy.orm import composite

from universal_bot.domain.entity.transcription import Transcription
from universal_bot.domain.enum.transcription.state import TranscriptionState
from universal_bot.domain.value_object.auth.failure_reason import FailureReason
from universal_bot.domain.value_object.messaging.message_id import TelegramMessageId
from universal_bot.domain.value_object.messaging.telegram_file_id import TelegramFileId
from universal_bot.domain.value_object.messaging.text import MessageText
from universal_bot.domain.value_object.time.timestamp import Timestamp
from universal_bot.domain.value_object.transcription.id import TranscriptionId
from universal_bot.domain.value_object.user.id import TelegramUserId
from universal_bot.infrastructure.persistence.sqla.registry import mapping_registry
from universal_bot.infrastructure.persistence.sqla.table.transcription import (
    transcription_table,
)
from universal_bot.infrastructure.persistence.sqla.type import EnumStringType


def map_transcription_table() -> None:
    transcription_table.c.state.type = EnumStringType(TranscriptionState)
    mapping_registry.map_imperatively(
        Transcription,
        transcription_table,
        properties={
            "_id": composite(TranscriptionId, transcription_table.c.id),
            "owner_id": composite(TelegramUserId, transcription_table.c.owner_id),
            "chat_id": composite(TelegramUserId, transcription_table.c.chat_id),
            "message_id": composite(
                TelegramMessageId, transcription_table.c.message_id
            ),
            "telegram_file_id": composite(
                TelegramFileId, transcription_table.c.telegram_file_id
            ),
            "created_at": composite(Timestamp, transcription_table.c.created_at),
            "_state": transcription_table.c.state,
            "text": composite(MessageText.from_raw, transcription_table.c.text),
            "error": composite(FailureReason.from_raw, transcription_table.c.error),
            "response_message_id": composite(
                TelegramMessageId.from_raw, transcription_table.c.response_message_id
            ),
            "finished_at": composite(
                Timestamp.from_raw, transcription_table.c.finished_at
            ),
        },
        column_prefix="_raw_",
    )
