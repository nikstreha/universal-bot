from collections.abc import Sequence

from sqlalchemy import select

from universal_bot.application.port.persistence.repository.transcription.writer import (
    ITranscriptionWriter,
)
from universal_bot.domain.common.util import convert_to_primitive
from universal_bot.domain.entity.transcription import Transcription
from universal_bot.domain.enum.transcription.state import TranscriptionState
from universal_bot.domain.value_object.messaging.message_id import TelegramMessageId
from universal_bot.domain.value_object.time.timestamp import Timestamp
from universal_bot.domain.value_object.transcription.id import TranscriptionId
from universal_bot.domain.value_object.user.id import TelegramUserId
from universal_bot.infrastructure.persistence.sqla.table.transcription import (
    transcription_table,
)
from universal_bot.infrastructure.persistence.sqla.type import WriterSession


class SQLATranscriptionWriter(ITranscriptionWriter):
    def __init__(self, session: WriterSession) -> None:
        self._session = session

    async def find_by_chat_id_and_message_id(
        self, *, chat_id: TelegramUserId, message_id: TelegramMessageId
    ) -> Transcription | None:
        chat_id_raw = convert_to_primitive(chat_id)
        message_id_raw = convert_to_primitive(message_id)
        statement = select(Transcription)
        statement = statement.where(
            transcription_table.c.chat_id == chat_id_raw,
            transcription_table.c.message_id == message_id_raw,
        )
        return (await self._session.scalars(statement.limit(1))).first()

    async def list_by_states(
        self, *, states: Sequence[TranscriptionState]
    ) -> list[Transcription]:
        states_raw = convert_to_primitive(states)
        statement = select(Transcription)
        statement = statement.where(transcription_table.c.state.in_(states_raw))
        return list(await self._session.scalars(statement))

    async def add(self, *, entity: Transcription) -> None:
        self._session.add(entity)
        await self._session.flush()

    async def find_by_id(self, *, key: TranscriptionId) -> Transcription | None:
        key_raw = convert_to_primitive(key)
        return await self._session.get(Transcription, key_raw)

    async def cancel_for_user(self, *, user_id: TelegramUserId, at: Timestamp) -> None:
        statement = select(Transcription).where(
            transcription_table.c.owner_id == user_id.value,
            transcription_table.c.state.in_(("accepted", "transcribing", "delivering")),
        )
        for row in await self._session.scalars(statement):
            row.cancel(at)
