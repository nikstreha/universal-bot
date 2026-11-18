from universal_bot.application.dto.telegram.delivery import AuthorizedDeliveryDTO
from universal_bot.application.port.clock import IClock
from universal_bot.application.port.persistence.repository.delivery.writer import (
    IDeliveryWriter,
)
from universal_bot.application.port.persistence.repository.transcription.writer import (
    ITranscriptionWriter,
)
from universal_bot.application.port.persistence.uow import IUnitOfWork
from universal_bot.application.service.access.access_policy import AccessPolicy
from universal_bot.domain.enum.transcription.state import TranscriptionState
from universal_bot.domain.value_object.delivery.id import DeliveryId
from universal_bot.domain.value_object.time.timestamp import Timestamp
from universal_bot.domain.value_object.transcription.id import TranscriptionId


class AuthorizeDeliveryInteractor:
    def __init__(
        self,
        *,
        access_policy: AccessPolicy,
        clock: IClock,
        delivery_writer: IDeliveryWriter,
        transcription_writer: ITranscriptionWriter,
        uow: IUnitOfWork,
    ) -> None:
        self._access_policy = access_policy
        self._clock = clock
        self._delivery_writer = delivery_writer
        self._transcription_writer = transcription_writer
        self._uow = uow

    async def __call__(
        self, *, delivery_id: str, lease_until: int
    ) -> AuthorizedDeliveryDTO | None:
        async with self._uow:
            row = await self._delivery_writer.find_by_id(key=DeliveryId(delivery_id))
            if row is None or not row.can_send(
                Timestamp(lease_until), Timestamp(self._clock.now())
            ):
                return None
            if (
                row.user_id is None
                or row.chat_id != row.user_id
                or (not await self._access_policy.allowed(user_id=row.user_id.value))
            ):
                row.cancel()
                return None
            text = row.text.value
            filename = row.filename
            target = None
            if row.dedup_key.value.startswith("transcription:"):
                transcription = await self._transcription_writer.find_by_id(
                    key=TranscriptionId(row.dedup_key.value.split(":")[1])
                )
                if (
                    transcription is None
                    or transcription.state is TranscriptionState.CANCELLED
                    or transcription.owner_id != row.user_id
                    or transcription.chat_id != row.chat_id
                ):
                    row.cancel()
                    return None
                target = transcription.response_message_id
                stage = row.dedup_key.value.rsplit(":", 1)[-1]
                if (stage == "accepted" and target is not None) or (
                    stage == "processing"
                    and transcription.state is not TranscriptionState.TRANSCRIBING
                ):
                    row.cancel()
                    return None
                filename = None
                if transcription.state is TranscriptionState.ACCEPTED:
                    text = "Аудио в очереди на расшифровку."
                elif transcription.state is TranscriptionState.TRANSCRIBING:
                    text = "Расшифровываю аудио…"
                elif transcription.state in (
                    TranscriptionState.DELIVERING,
                    TranscriptionState.COMPLETED,
                ):
                    content = transcription.text.value if transcription.text else ""
                    content = content or "В аудио не обнаружена речь."
                    text = "Готово.\n\n" + content
                    if len(text.encode("utf-16-le")) // 2 > 4000:
                        text = content
                        filename = "transcription.txt"
                else:
                    text = "Не удалось расшифровать аудио. Попробуйте отправить файл повторно."
            return AuthorizedDeliveryDTO(
                id=str(row.id_.value),
                chat_id=row.chat_id.value,
                text=text,
                lease_until=lease_until,
                created_at=row.created_at.value,
                filename=filename,
                reply_to=row.reply_to.value if row.reply_to else None,
                edit_message_id=target.value if target else None,
            )
