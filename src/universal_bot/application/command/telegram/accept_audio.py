from universal_bot.application.exception.common import (
    FileTooLargeError,
    LimitReachedError,
)
from universal_bot.application.port.clock import IClock
from universal_bot.application.port.persistence.repository.job.writer import IJobWriter
from universal_bot.application.port.persistence.repository.transcription.writer import (
    ITranscriptionWriter,
)
from universal_bot.application.port.persistence.uow import IUnitOfWork
from universal_bot.application.port.security.secrets import ISecrets
from universal_bot.application.service.access.access_policy import AccessPolicy
from universal_bot.domain.common.guard import ensure
from universal_bot.domain.entity.job import Job
from universal_bot.domain.entity.transcription import Transcription
from universal_bot.domain.enum.job.kind import JobKind
from universal_bot.domain.enum.transcription.state import TranscriptionState
from universal_bot.domain.exception.common import InvalidRequestError
from universal_bot.domain.value_object.job.id import JobId
from universal_bot.domain.value_object.job.resource_id import ResourceId
from universal_bot.domain.value_object.messaging.message_id import TelegramMessageId
from universal_bot.domain.value_object.messaging.telegram_file_id import TelegramFileId
from universal_bot.domain.value_object.time.timestamp import Timestamp
from universal_bot.domain.value_object.transcription.id import TranscriptionId
from universal_bot.domain.value_object.user.id import TelegramUserId


class AcceptAudioInteractor:
    def __init__(
        self,
        *,
        access_policy: AccessPolicy,
        clock: IClock,
        secrets: ISecrets,
        transcription_writer: ITranscriptionWriter,
        uow: IUnitOfWork,
        job_writer: IJobWriter,
    ) -> None:
        self._access_policy = access_policy
        self._clock = clock
        self._secrets = secrets
        self._transcription_writer = transcription_writer
        self._uow = uow
        self._job_writer = job_writer

    async def __call__(
        self,
        *,
        user_id: int,
        chat_id: int,
        message_id: int,
        file_id: str,
        size: int | None,
    ) -> tuple[Transcription, bool]:
        ensure(
            chat_id == user_id,
            InvalidRequestError,
            "Аудио принимается только из личного чата владельца",
        )
        ensure(
            size is not None and 0 < size <= 20000000,
            FileTooLargeError,
            "Пришлите аудио не больше 20 МБ",
        )
        async with self._uow:
            await self._access_policy.require_access(user_id=user_id)
            existing = await self._transcription_writer.find_by_chat_id_and_message_id(
                chat_id=TelegramUserId(chat_id),
                message_id=TelegramMessageId(message_id),
            )
            if existing:
                return (existing, False)
            active = await self._transcription_writer.list_by_states(
                states=(
                    TranscriptionState.ACCEPTED,
                    TranscriptionState.TRANSCRIBING,
                    TranscriptionState.DELIVERING,
                )
            )
            ensure(
                len(active) < 50
                and sum(row.owner_id.value == user_id for row in active) < 3,
                LimitReachedError,
                "Очередь заполнена. Дождитесь результата",
            )
            row = Transcription(
                id_=TranscriptionId(self._secrets.identity()),
                owner_id=TelegramUserId(user_id),
                chat_id=TelegramUserId(chat_id),
                message_id=TelegramMessageId(message_id),
                telegram_file_id=TelegramFileId(file_id),
                created_at=Timestamp(self._clock.now()),
            )
            await self._transcription_writer.add(entity=row)
            task = Job.create(
                id_=JobId(self._secrets.identity()),
                kind=JobKind("transcribe"),
                resource_id=ResourceId(str(row.id_.value)),
                at=Timestamp(self._clock.now()),
            )
            if not await self._job_writer.find_by_dedup_key(dedup_key=task.dedup_key):
                await self._job_writer.add(entity=task)
            return (row, True)
