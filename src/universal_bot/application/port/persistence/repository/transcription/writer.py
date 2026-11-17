from abc import ABC, abstractmethod
from collections.abc import Sequence

from universal_bot.domain.entity.transcription import Transcription
from universal_bot.domain.enum.transcription.state import TranscriptionState
from universal_bot.domain.value_object.messaging.message_id import TelegramMessageId
from universal_bot.domain.value_object.time.timestamp import Timestamp
from universal_bot.domain.value_object.transcription.id import TranscriptionId
from universal_bot.domain.value_object.user.id import TelegramUserId


class ITranscriptionWriter(ABC):
    @abstractmethod
    async def find_by_chat_id_and_message_id(
        self, *, chat_id: TelegramUserId, message_id: TelegramMessageId
    ) -> Transcription | None: ...

    @abstractmethod
    async def list_by_states(
        self, *, states: Sequence[TranscriptionState]
    ) -> list[Transcription]: ...

    @abstractmethod
    async def add(self, *, entity: Transcription) -> None: ...

    @abstractmethod
    async def find_by_id(self, *, key: TranscriptionId) -> Transcription | None: ...

    @abstractmethod
    async def cancel_for_user(
        self, *, user_id: TelegramUserId, at: Timestamp
    ) -> None: ...
