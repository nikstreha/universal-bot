from universal_bot.domain.entity.common import Entity
from universal_bot.domain.enum.transcription.state import TranscriptionState
from universal_bot.domain.exception.common import InvalidRequestError, InvalidStateError
from universal_bot.domain.value_object.auth.failure_reason import FailureReason
from universal_bot.domain.value_object.messaging.message_id import TelegramMessageId
from universal_bot.domain.value_object.messaging.telegram_file_id import TelegramFileId
from universal_bot.domain.value_object.messaging.text import MessageText
from universal_bot.domain.value_object.time.timestamp import Timestamp
from universal_bot.domain.value_object.transcription.id import TranscriptionId
from universal_bot.domain.value_object.user.id import TelegramUserId


class Transcription(Entity[TranscriptionId]):
    _id: TranscriptionId
    owner_id: TelegramUserId
    chat_id: TelegramUserId
    message_id: TelegramMessageId
    telegram_file_id: TelegramFileId
    created_at: Timestamp
    state: TranscriptionState
    text: MessageText | None
    error: FailureReason | None
    delivered_message_id: TelegramMessageId | None
    finished_at: Timestamp | None

    def __init__(
        self,
        *,
        id_: TranscriptionId,
        owner_id: TelegramUserId,
        chat_id: TelegramUserId,
        message_id: TelegramMessageId,
        telegram_file_id: TelegramFileId,
        created_at: Timestamp,
        state: TranscriptionState = TranscriptionState.ACCEPTED,
        text: MessageText | None = None,
        error: FailureReason | None = None,
        delivered_message_id: TelegramMessageId | None = None,
        finished_at: Timestamp | None = None,
    ) -> None:
        super().__init__(id_=id_)
        self.owner_id = owner_id
        self.chat_id = chat_id
        self.message_id = message_id
        self.telegram_file_id = telegram_file_id
        self.created_at = created_at
        self._state = state
        self.text = text
        self.error = error
        self.delivered_message_id = delivered_message_id
        self.finished_at = finished_at

    @property
    def state(self) -> TranscriptionState:
        return self._state

    def start(self, at: Timestamp) -> bool:
        if self.state not in (
            TranscriptionState.ACCEPTED,
            TranscriptionState.TRANSCRIBING,
        ):
            return False
        if self.owner_id != self.chat_id:
            raise InvalidRequestError("Аудио должно принадлежать владельцу чата")
        self._state = TranscriptionState.TRANSCRIBING
        return True

    def finish(self, text: MessageText, at: Timestamp) -> bool:
        if self.state is TranscriptionState.CANCELLED:
            return False
        if self.state is not TranscriptionState.TRANSCRIBING:
            raise InvalidStateError("Аудио не обрабатывается")
        self._state, self.text, self.finished_at = (
            TranscriptionState.DELIVERING,
            text,
            at,
        )
        return True

    def fail(self, reason: FailureReason, at: Timestamp) -> bool:
        if self.state is TranscriptionState.CANCELLED:
            return False
        self._state, self.error, self.finished_at = (
            TranscriptionState.FAILED,
            reason,
            at,
        )
        return True

    def cancel(self, at: Timestamp) -> None:
        if self.state in (
            TranscriptionState.ACCEPTED,
            TranscriptionState.TRANSCRIBING,
            TranscriptionState.DELIVERING,
        ):
            self._state, self.text, self.finished_at = (
                TranscriptionState.CANCELLED,
                None,
                at,
            )

    def delivered(self, message_id: TelegramMessageId | None, terminal: bool) -> None:
        if self.state is TranscriptionState.CANCELLED:
            return
        self.delivered_message_id = message_id
        self._state = (
            TranscriptionState.FAILED if terminal else TranscriptionState.COMPLETED
        )
