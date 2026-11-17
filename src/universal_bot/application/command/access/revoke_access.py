import logging

from universal_bot.application.dto.common.policy import Policy
from universal_bot.application.exception.common import AdminProtectedError
from universal_bot.application.port.clock import IClock
from universal_bot.application.port.persistence.repository.access_grant.writer import (
    IAccessGrantWriter,
)
from universal_bot.application.port.persistence.repository.audit_event.writer import (
    IAuditEventWriter,
)
from universal_bot.application.port.persistence.repository.delivery.writer import (
    IDeliveryWriter,
)
from universal_bot.application.port.persistence.repository.session.writer import (
    ISessionWriter,
)
from universal_bot.application.port.persistence.repository.transcription.writer import (
    ITranscriptionWriter,
)
from universal_bot.application.port.persistence.repository.upload.writer import (
    IUploadWriter,
)
from universal_bot.application.port.persistence.uow import IUnitOfWork
from universal_bot.application.port.security.secrets import ISecrets
from universal_bot.application.service.access.access_policy import AccessPolicy
from universal_bot.domain.common.guard import ensure
from universal_bot.domain.entity.audit_event import AuditEvent
from universal_bot.domain.enum.access.action import AccessAction
from universal_bot.domain.enum.upload.state import UploadState
from universal_bot.domain.value_object.audit_event.id import AuditEventId
from universal_bot.domain.value_object.time.timestamp import Timestamp
from universal_bot.domain.value_object.user.id import TelegramUserId


class RevokeAccessInteractor:
    def __init__(
        self,
        *,
        access_grant_writer: IAccessGrantWriter,
        delivery_writer: IDeliveryWriter,
        transcription_writer: ITranscriptionWriter,
        access_policy: AccessPolicy,
        audit_event_writer: IAuditEventWriter,
        clock: IClock,
        policy: Policy,
        secrets: ISecrets,
        session_writer: ISessionWriter,
        uow: IUnitOfWork,
        upload_writer: IUploadWriter,
    ) -> None:
        self._access_grant_writer = access_grant_writer
        self._delivery_writer = delivery_writer
        self._transcription_writer = transcription_writer
        self._access_policy = access_policy
        self._audit_event_writer = audit_event_writer
        self._clock = clock
        self._policy = policy
        self._secrets = secrets
        self._session_writer = session_writer
        self._uow = uow
        self._upload_writer = upload_writer

    async def __call__(self, *, actor_id: int, user_id: int) -> None:
        await self._access_policy.require_admin(actor_id=actor_id)
        ensure(
            user_id != self._policy.admin_id,
            AdminProtectedError,
            "Нельзя удалить администратора",
        )
        async with self._uow:
            grant = await self._access_grant_writer.find_by_id(
                key=TelegramUserId(user_id)
            )
            if grant:
                await self._access_grant_writer.delete(entity=grant)
            for session in await self._session_writer.list_by_user_id(
                user_id=TelegramUserId(user_id), revoked_at=None
            ):
                session.revoke(Timestamp(self._clock.now()))
            for upload in await self._upload_writer.list_by_owner_and_states(
                owner_id=TelegramUserId(user_id),
                states=(UploadState.RECEIVING, UploadState.VERIFYING),
            ):
                upload.cancel()
            await self._delivery_writer.cancel_for_user(
                user_id=TelegramUserId(user_id), at=Timestamp(self._clock.now())
            )
            await self._transcription_writer.cancel_for_user(
                user_id=TelegramUserId(user_id), at=Timestamp(self._clock.now())
            )
            await self._audit_event_writer.add(
                entity=AuditEvent(
                    id_=AuditEventId(self._secrets.identity()),
                    actor_id=TelegramUserId(actor_id),
                    target_id=TelegramUserId(user_id),
                    action=AccessAction.REVOKE,
                    created_at=Timestamp(self._clock.now()),
                )
            )

        logging.getLogger(__name__).info(
            "User access changed",
            extra={
                "event": "admin_action",
                "actor_id": actor_id,
                "target_id": user_id,
                "operation": "revoke_access",
            },
        )
