from universal_bot.application.port.clock import IClock
from universal_bot.application.port.persistence.repository.admin_notification.writer import (
    IAdminNotificationWriter,
)
from universal_bot.application.port.persistence.repository.login_attempt.writer import (
    ILoginAttemptWriter,
)
from universal_bot.application.port.persistence.uow import IUnitOfWork
from universal_bot.application.port.security.secrets import ISecrets
from universal_bot.application.service.access.access_policy import AccessPolicy
from universal_bot.domain.common.guard import ensure
from universal_bot.domain.entity.admin_notification import AdminNotification
from universal_bot.domain.enum.access.source import AccessSource
from universal_bot.domain.enum.login_attempt.status import LoginAttemptStatus
from universal_bot.domain.enum.notification.outcome import LoginOutcome
from universal_bot.domain.exception.auth import InvalidLoginError
from universal_bot.domain.value_object.login_attempt.id import LoginAttemptId
from universal_bot.domain.value_object.notification.event_key import EventKey
from universal_bot.domain.value_object.notification.id import NotificationId
from universal_bot.domain.value_object.time.timestamp import Timestamp
from universal_bot.domain.value_object.user.id import TelegramUserId


class ConfirmLoginAttemptInteractor:
    def __init__(
        self,
        *,
        access_policy: AccessPolicy,
        admin_notification_writer: IAdminNotificationWriter,
        clock: IClock,
        login_attempt_writer: ILoginAttemptWriter,
        secrets: ISecrets,
        uow: IUnitOfWork,
    ) -> None:
        self._access_policy = access_policy
        self._admin_notification_writer = admin_notification_writer
        self._clock = clock
        self._login_attempt_writer = login_attempt_writer
        self._secrets = secrets
        self._uow = uow

    async def __call__(
        self, *, attempt_id: str, user_id: int, accepted: bool
    ) -> LoginAttemptStatus:
        async with self._uow:
            attempt = await self._login_attempt_writer.find_by_id(
                key=LoginAttemptId(attempt_id)
            )
            ensure(
                attempt and attempt.candidate_id == TelegramUserId(user_id),
                InvalidLoginError,
                "Подтвердите вход со своего аккаунта",
            )
            if accepted:
                allowed = await self._access_policy.allowed(user_id=user_id)
                attempt.confirm(
                    TelegramUserId(user_id),
                    allowed,
                    Timestamp(self._clock.now()),
                )
                await self._admin_notification_writer.add(
                    entity=AdminNotification(
                        id_=NotificationId(self._secrets.identity()),
                        event_key=EventKey(f"app:{str(attempt.id_.value)}"),
                        user_id=TelegramUserId(user_id),
                        source=AccessSource.APP,
                        outcome=LoginOutcome.ALLOWED
                        if allowed
                        else LoginOutcome.DENIED,
                        created_at=Timestamp(self._clock.now()),
                    )
                )
            else:
                attempt.cancel(TelegramUserId(user_id), Timestamp(self._clock.now()))
            return attempt.status
