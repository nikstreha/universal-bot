import logging

from universal_bot.application.exception.common import InvalidUserIdError
from universal_bot.application.port.clock import IClock
from universal_bot.application.port.persistence.repository.access_grant.writer import (
    IAccessGrantWriter,
)
from universal_bot.application.port.persistence.repository.access_request.writer import (
    IAccessRequestWriter,
)
from universal_bot.application.port.persistence.repository.audit_event.writer import (
    IAuditEventWriter,
)
from universal_bot.application.port.persistence.repository.user.writer import (
    IUserWriter,
)
from universal_bot.application.port.persistence.uow import IUnitOfWork
from universal_bot.application.port.security.secrets import ISecrets
from universal_bot.application.service.access.access_policy import AccessPolicy
from universal_bot.domain.common.guard import ensure
from universal_bot.domain.entity.access_grant import AccessGrant
from universal_bot.domain.entity.audit_event import AuditEvent
from universal_bot.domain.entity.user import User
from universal_bot.domain.enum.access.action import AccessAction
from universal_bot.domain.value_object.audit_event.id import AuditEventId
from universal_bot.domain.value_object.time.timestamp import Timestamp
from universal_bot.domain.value_object.user.id import TelegramUserId
from universal_bot.domain.value_object.user.name import UserName


class GrantAccessInteractor:
    def __init__(
        self,
        *,
        access_grant_writer: IAccessGrantWriter,
        access_policy: AccessPolicy,
        access_request_writer: IAccessRequestWriter,
        audit_event_writer: IAuditEventWriter,
        clock: IClock,
        secrets: ISecrets,
        uow: IUnitOfWork,
        user_writer: IUserWriter,
    ) -> None:
        self._access_grant_writer = access_grant_writer
        self._access_policy = access_policy
        self._access_request_writer = access_request_writer
        self._audit_event_writer = audit_event_writer
        self._clock = clock
        self._secrets = secrets
        self._uow = uow
        self._user_writer = user_writer

    async def __call__(self, *, actor_id: int, user_id: int) -> None:
        await self._access_policy.require_admin(actor_id=actor_id)
        ensure(0 < user_id < 2**63, InvalidUserIdError, "Неверный Telegram ID")
        async with self._uow:
            user = await self._user_writer.find_by_id(key=TelegramUserId(user_id))
            user_at = Timestamp(self._clock.now())
            if user is None:
                user = User(
                    id_=TelegramUserId(user_id),
                    name=UserName(""),
                    created_at=user_at,
                    last_seen_at=user_at,
                )
                await self._user_writer.add(entity=user)
            else:
                user.touch(UserName(""), user_at)
            if not await self._access_grant_writer.find_by_id(
                key=TelegramUserId(user_id)
            ):
                await self._access_grant_writer.add(
                    entity=AccessGrant(
                        user_id=TelegramUserId(user_id),
                        added_at=Timestamp(self._clock.now()),
                        added_by=TelegramUserId(actor_id),
                    )
                )
            request = await self._access_request_writer.find_by_user_id(
                user_id=TelegramUserId(user_id)
            )
            if request is not None:
                request.mark_access_granted(
                    TelegramUserId(actor_id), Timestamp(self._clock.now())
                )
            await self._audit_event_writer.add(
                entity=AuditEvent(
                    id_=AuditEventId(self._secrets.identity()),
                    actor_id=TelegramUserId(actor_id),
                    target_id=TelegramUserId(user_id),
                    action=AccessAction.GRANT,
                    created_at=Timestamp(self._clock.now()),
                )
            )

        logging.getLogger(__name__).info(
            "User access changed",
            extra={
                "event": "admin_action",
                "actor_id": actor_id,
                "target_id": user_id,
                "operation": "grant_access",
            },
        )
