from universal_bot.application.port.clock import IClock
from universal_bot.application.port.persistence.repository.delivery.writer import (
    IDeliveryWriter,
)
from universal_bot.application.port.persistence.repository.job.writer import IJobWriter
from universal_bot.application.port.persistence.repository.stored_file.writer import (
    IStoredFileWriter,
)
from universal_bot.application.port.persistence.repository.transcription.writer import (
    ITranscriptionWriter,
)
from universal_bot.application.port.persistence.repository.upload.writer import (
    IUploadWriter,
)
from universal_bot.application.port.persistence.repository.verification.writer import (
    IVerificationWriter,
)
from universal_bot.application.port.persistence.uow import IUnitOfWork
from universal_bot.application.port.security.secrets import ISecrets
from universal_bot.domain.common.guard import ensure
from universal_bot.domain.entity.delivery import Delivery
from universal_bot.domain.entity.job import Job
from universal_bot.domain.enum.job.kind import JobKind
from universal_bot.domain.exception.job import LeaseLostError
from universal_bot.domain.value_object.auth.failure_reason import FailureReason
from universal_bot.domain.value_object.delivery.id import DeliveryId
from universal_bot.domain.value_object.messaging.text import MessageText
from universal_bot.domain.value_object.stored_file.id import StoredFileId
from universal_bot.domain.value_object.time.timestamp import Timestamp
from universal_bot.domain.value_object.transcription.id import TranscriptionId
from universal_bot.domain.value_object.upload.id import UploadId
from universal_bot.domain.value_object.verification.id import VerificationId


class FinishJobInteractor:
    def __init__(
        self,
        *,
        clock: IClock,
        transcription_writer: ITranscriptionWriter,
        uow: IUnitOfWork,
        upload_writer: IUploadWriter,
        verification_writer: IVerificationWriter,
        stored_file_writer: IStoredFileWriter,
        job_writer: IJobWriter,
        delivery_writer: IDeliveryWriter,
        secrets: ISecrets,
    ) -> None:
        self._clock = clock
        self._transcription_writer = transcription_writer
        self._uow = uow
        self._upload_writer = upload_writer
        self._verification_writer = verification_writer
        self._stored_file_writer = stored_file_writer
        self._job_writer = job_writer
        self._delivery_writer = delivery_writer
        self._secrets = secrets

    async def __call__(self, *, job: Job, error: Exception | None = None) -> None:
        async with self._uow:
            fresh = await self._job_writer.find_by_id(key=job.id_)
            ensure(fresh, LeaseLostError, "Задача не найдена")
            at = Timestamp(self._clock.now())
            fresh.validate_lease(job.generation, at)
            if error is None:
                fresh.succeed()
                return
            if getattr(error, "code", "") == "LEASE_LOST":
                raise error
            reason = FailureReason(getattr(error, "code", type(error).__name__))
            if not fresh.fail(reason, at):
                return
            if fresh.kind is JobKind.FINALIZE:
                upload = await self._upload_writer.find_by_id(
                    key=UploadId(fresh.resource_id.value)
                )
                if upload is not None:
                    upload.fail(reason)
            elif fresh.kind is JobKind.VERIFY:
                check = await self._verification_writer.find_by_id(
                    key=VerificationId(fresh.resource_id.value)
                )
                if check is not None:
                    check.fail(reason, at)
            elif fresh.kind is JobKind.THUMBNAIL:
                file = await self._stored_file_writer.find_by_id(
                    key=StoredFileId(fresh.resource_id.value)
                )
                if file is not None:
                    file.thumbnail_failed()
            elif fresh.kind is JobKind.TRANSCRIBE:
                row = await self._transcription_writer.find_by_id(
                    key=TranscriptionId(fresh.resource_id.value)
                )
                if row is not None and row.fail(reason, at):
                    delivery = Delivery.for_transcription(
                        id_=DeliveryId(self._secrets.identity()),
                        transcription=row,
                        text=MessageText(
                            "Не удалось расшифровать аудио. Попробуйте отправить файл повторно."
                        ),
                        at=at,
                        suffix="error",
                    )
                    if not await self._delivery_writer.find_by_dedup_key(
                        dedup_key=delivery.dedup_key
                    ):
                        await self._delivery_writer.add(entity=delivery)
