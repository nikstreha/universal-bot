from universal_bot.application.port.clock import IClock
from universal_bot.application.port.persistence.repository.delivery.writer import (
    IDeliveryWriter,
)
from universal_bot.application.port.persistence.repository.transcription.writer import (
    ITranscriptionWriter,
)
from universal_bot.application.port.persistence.uow import IUnitOfWork
from universal_bot.domain.value_object.delivery.id import DeliveryId
from universal_bot.domain.value_object.messaging.message_id import TelegramMessageId
from universal_bot.domain.value_object.time.timestamp import Timestamp
from universal_bot.domain.value_object.transcription.id import TranscriptionId


class CompleteDeliveryInteractor:
    def __init__(
        self,
        *,
        clock: IClock,
        delivery_writer: IDeliveryWriter,
        transcription_writer: ITranscriptionWriter,
        uow: IUnitOfWork,
    ) -> None:
        self._clock = clock
        self._delivery_writer = delivery_writer
        self._transcription_writer = transcription_writer
        self._uow = uow

    async def __call__(
        self,
        *,
        delivery_id: str,
        lease_until: int,
        message_id: int | None = None,
        retry_after: int | None = None,
        terminal: bool = False,
    ) -> None:
        async with self._uow:
            row = await self._delivery_writer.find_by_id(key=DeliveryId(delivery_id))
            if row is None or not row.owns_lease(Timestamp(lease_until)):
                return
            if retry_after is not None:
                row.retry(
                    Timestamp(lease_until), Timestamp(self._clock.now()), retry_after
                )
                return
            delivered_id = TelegramMessageId.from_raw(message_id)
            if not row.complete(Timestamp(lease_until), delivered_id, terminal):
                return
            if row.dedup_key.value.startswith("transcription:"):
                transcription = await self._transcription_writer.find_by_id(
                    key=TranscriptionId(row.dedup_key.value.split(":")[1])
                )
                if transcription is not None:
                    transcription.delivered(delivered_id, terminal)
