from universal_bot.application.dto.common.policy import Policy
from universal_bot.application.exception.common import (
    AuthAttemptExpiredError,
    NotWhitelistedError,
)
from universal_bot.application.port.clock import IClock
from universal_bot.application.port.persistence.repository.access_request.writer import (
    IAccessRequestWriter,
)
from universal_bot.application.port.persistence.repository.login_attempt.writer import (
    ILoginAttemptWriter,
)
from universal_bot.application.port.persistence.repository.session.writer import (
    ISessionWriter,
)
from universal_bot.application.port.persistence.repository.user.writer import (
    IUserWriter,
)
from universal_bot.application.port.persistence.uow import IUnitOfWork
from universal_bot.application.port.security.secrets import ISecrets
from universal_bot.application.query_model.login import (
    AuthenticatedSessionQueryModel,
    LoginUserQueryModel,
    PendingLoginQueryModel,
)
from universal_bot.application.service.access.access_policy import AccessPolicy
from universal_bot.domain.common.guard import ensure
from universal_bot.domain.entity.session import Session
from universal_bot.domain.enum.login_attempt.status import LoginAttemptStatus
from universal_bot.domain.exception.auth import LoginCancelledError
from universal_bot.domain.value_object.auth.code_challenge import CodeChallenge
from universal_bot.domain.value_object.auth.token_hash import TokenHash
from universal_bot.domain.value_object.login_attempt.id import LoginAttemptId
from universal_bot.domain.value_object.session.id import SessionId
from universal_bot.domain.value_object.time.timestamp import Timestamp


class ExchangeLoginAttemptInteractor:
    def __init__(
        self,
        *,
        access_policy: AccessPolicy,
        access_request_writer: IAccessRequestWriter,
        clock: IClock,
        policy: Policy,
        secrets: ISecrets,
        session_writer: ISessionWriter,
        uow: IUnitOfWork,
        user_writer: IUserWriter,
        login_attempt_writer: ILoginAttemptWriter,
    ) -> None:
        self._access_policy = access_policy
        self._access_request_writer = access_request_writer
        self._clock = clock
        self._policy = policy
        self._secrets = secrets
        self._session_writer = session_writer
        self._uow = uow
        self._user_writer = user_writer
        self._login_attempt_writer = login_attempt_writer

    async def __call__(
        self, *, attempt_id: str, verifier: str
    ) -> PendingLoginQueryModel | AuthenticatedSessionQueryModel:
        async with self._uow:
            attempt = await self._login_attempt_writer.find_by_id(
                key=LoginAttemptId(attempt_id)
            )
            ensure(attempt, AuthAttemptExpiredError, "Войдите через Telegram ещё раз")
            attempt.require_proof(
                CodeChallenge(self._secrets.challenge(verifier)),
                Timestamp(self._clock.now()),
            )
            if attempt.status is LoginAttemptStatus.PENDING:
                return PendingLoginQueryModel()
            ensure(
                attempt.status in (LoginAttemptStatus.READY, LoginAttemptStatus.DENIED),
                LoginCancelledError,
                "Вход отменён",
            )
            user_id = attempt.confirmed_user(Timestamp(self._clock.now()))
            request = await self._access_request_writer.find_by_user_id(user_id=user_id)
            ensure(
                attempt.status is LoginAttemptStatus.READY
                and await self._access_policy.allowed(user_id=user_id.value),
                NotWhitelistedError,
                "Доступ пока не открыт",
                attempt_id=str(attempt.id_.value),
                telegram_id=str(user_id.value),
                access_request_status=request.status if request else "not_requested",
                can_request_access=request is None,
            )
            now = self._clock.now()
            secret = self._secrets.token()
            session = Session.create(
                id_=SessionId(self._secrets.identity()),
                user_id=user_id,
                token_hash=TokenHash(self._secrets.hash(secret)),
                installation_id=attempt.installation_id,
                device_name=attempt.device_name,
                at=Timestamp(now),
                idle_seconds=self._policy.session_idle_seconds,
                max_seconds=self._policy.session_max_seconds,
            )
            await self._session_writer.add(entity=session)
            attempt.consume(Timestamp(now))
            user = await self._user_writer.find_by_id(key=user_id)
            return AuthenticatedSessionQueryModel(
                session_token=secret,
                session_id=str(session.id_.value),
                expires_at=session.expires_at.value,
                absolute_expires_at=session.absolute_expires_at.value,
                user=LoginUserQueryModel(
                    id=str(user.id_.value),
                    name=user.name.value,
                    is_admin=user.id_.value == self._policy.admin_id,
                ),
            )
