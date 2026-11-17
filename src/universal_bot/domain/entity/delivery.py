from universal_bot.domain.entity.common import Entity
from universal_bot.domain.entity.transcription import Transcription
from universal_bot.domain.enum.delivery.state import DeliveryState
from universal_bot.domain.exception.common import InvalidRequestError
from universal_bot.domain.exception.job import LeaseLostError
from universal_bot.domain.value_object.delivery.id import DeliveryId
from universal_bot.domain.value_object.job.deduplication_key import DeduplicationKey
from universal_bot.domain.value_object.messaging.message_id import TelegramMessageId
from universal_bot.domain.value_object.messaging.text import MessageText
from universal_bot.domain.value_object.time.timestamp import Timestamp
from universal_bot.domain.value_object.user.id import TelegramUserId


class Delivery(Entity[DeliveryId]):
    _id: DeliveryId
    dedup_key: DeduplicationKey
    chat_id: TelegramUserId
    text: MessageText
    next_attempt_at: Timestamp
    created_at: Timestamp
    reply_to: TelegramMessageId | None
    filename: str | None
    user_id: TelegramUserId | None
    state: DeliveryState
    lease_until: Timestamp | None
    message_id: TelegramMessageId | None

    def __init__(
        self,
        *,
        id_: DeliveryId,
        dedup_key: DeduplicationKey,
        chat_id: TelegramUserId,
        text: MessageText,
        next_attempt_at: Timestamp,
        created_at: Timestamp,
        reply_to: TelegramMessageId | None = None,
        filename: str | None = None,
        user_id: TelegramUserId | None = None,
        state: DeliveryState = DeliveryState.QUEUED,
        lease_until: Timestamp | None = None,
        message_id: TelegramMessageId | None = None,
    ) -> None:
        super().__init__(id_=id_)
        self.dedup_key = dedup_key
        self.chat_id = chat_id
        self.text = text
        self.next_attempt_at = next_attempt_at
        self.created_at = created_at
        self.reply_to = reply_to
        self.filename = filename
        self.user_id = user_id
        self._state = state
        self.lease_until = lease_until
        self.message_id = message_id

    @property
    def state(self) -> DeliveryState:
        return self._state

    @classmethod
    def for_transcription(
        cls,
        *,
        id_: DeliveryId,
        transcription: Transcription,
        text: MessageText,
        at: Timestamp,
        suffix: str = "result",
    ) -> Delivery:
        if transcription.chat_id != transcription.owner_id:
            raise InvalidRequestError("Доставка разрешена только владельцу")
        return cls(
            id_=id_,
            dedup_key=DeduplicationKey(
                f"transcription:{transcription.id_.value}:{suffix}"
            ),
            chat_id=transcription.chat_id,
            user_id=transcription.owner_id,
            text=text,
            filename="transcription.txt" if len(text.value) > 3500 else None,
            reply_to=transcription.message_id,
            next_attempt_at=at,
            created_at=at,
        )

    def claim(self, at: Timestamp) -> None:
        expired = (
            self.state is DeliveryState.SENDING
            and self.lease_until is not None
            and (self.lease_until.value <= at.value)
        )
        if self.next_attempt_at.value > at.value or not (
            self.state is DeliveryState.QUEUED or expired
        ):
            raise LeaseLostError("Сообщение уже отправляется")
        if self.user_id is None or self.user_id != self.chat_id:
            raise InvalidRequestError("Неизвестный получатель")
        self._state, self.lease_until = (DeliveryState.SENDING, at.after(90))

    def owns_lease(self, lease_until: Timestamp) -> bool:
        return self.state is DeliveryState.SENDING and self.lease_until == lease_until

    def can_send(self, lease_until: Timestamp, at: Timestamp) -> bool:
        return self.owns_lease(lease_until) and lease_until.value > at.value

    def cancel(self) -> None:
        if self.state in (DeliveryState.QUEUED, DeliveryState.SENDING):
            self._state, self.text, self.lease_until = (
                DeliveryState.CANCELLED,
                MessageText(""),
                None,
            )

    def retry(self, lease_until: Timestamp, at: Timestamp, seconds: int) -> None:
        if self.owns_lease(lease_until):
            self._state, self.next_attempt_at = (
                DeliveryState.QUEUED,
                at.after(seconds),
            )

    def complete(
        self,
        lease_until: Timestamp,
        message_id: TelegramMessageId | None,
        terminal: bool,
    ) -> bool:
        if not self.owns_lease(lease_until):
            return False
        self._state = DeliveryState.FAILED if terminal else DeliveryState.COMPLETED
        self.message_id = message_id
        return True
