import asyncio

from universal_bot.application.port.clock import IClock
from universal_bot.application.port.persistence.repository.delivery.writer import (
    IDeliveryWriter,
)
from universal_bot.application.port.persistence.repository.job.writer import IJobWriter
from universal_bot.application.port.persistence.repository.transcription.writer import (
    ITranscriptionWriter,
)
from universal_bot.application.port.persistence.uow import IUnitOfWork
from universal_bot.application.port.security.secrets import ISecrets
from universal_bot.application.port.transcription.recognizer import ISpeechRecognizer
from universal_bot.application.service.access.access_policy import AccessPolicy
from universal_bot.domain.common.guard import ensure
from universal_bot.domain.entity.delivery import Delivery
from universal_bot.domain.entity.job import Job
from universal_bot.domain.exception.job import LeaseLostError
from universal_bot.domain.value_object.delivery.id import DeliveryId
from universal_bot.domain.value_object.messaging.text import MessageText
from universal_bot.domain.value_object.time.timestamp import Timestamp
from universal_bot.domain.value_object.transcription.id import TranscriptionId


class TranscribeAudioInteractor:
    def __init__(
        self,
        *,
        access_policy: AccessPolicy,
        clock: IClock,
        recognizer: ISpeechRecognizer,
        transcription_writer: ITranscriptionWriter,
        uow: IUnitOfWork,
        job_writer: IJobWriter,
        delivery_writer: IDeliveryWriter,
        secrets: ISecrets,
    ) -> None:
        self._access_policy = access_policy
        self._clock = clock
        self._recognizer = recognizer
        self._transcription_writer = transcription_writer
        self._uow = uow
        self._job_writer = job_writer
        self._delivery_writer = delivery_writer
        self._secrets = secrets

    async def __call__(self, *, job: Job) -> None:
        async with self._uow:
            current_job = await self._job_writer.find_by_id(key=job.id_)
            ensure(current_job, LeaseLostError, "Задача не найдена")
            at = Timestamp(self._clock.now())
            current_job.validate_lease(job.generation, at)
            row = await self._transcription_writer.find_by_id(
                key=TranscriptionId(job.resource_id.value)
            )
            if row is None:
                return
            if not await self._access_policy.allowed(user_id=row.owner_id.value):
                row.cancel(at)
                return
            if not row.start(at):
                return
        text = await asyncio.to_thread(
            self._recognizer.transcribe, row.telegram_file_id.value
        )
        async with self._uow:
            current_job = await self._job_writer.find_by_id(key=job.id_)
            ensure(current_job, LeaseLostError, "Задача не найдена")
            at = Timestamp(self._clock.now())
            current_job.validate_lease(job.generation, at)
            fresh = await self._transcription_writer.find_by_id(key=row.id_)
            if fresh is None:
                return
            if not await self._access_policy.allowed(user_id=fresh.owner_id.value):
                fresh.cancel(at)
                return
            if fresh.finish(MessageText(text), at):
                delivery = Delivery.for_transcription(
                    id_=DeliveryId(self._secrets.identity()),
                    transcription=fresh,
                    text=MessageText(text or "В аудио не обнаружена речь."),
                    at=at,
                )
                if not await self._delivery_writer.find_by_dedup_key(
                    dedup_key=delivery.dedup_key
                ):
                    await self._delivery_writer.add(entity=delivery)
