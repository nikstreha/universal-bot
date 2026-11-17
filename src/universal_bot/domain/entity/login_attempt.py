from hmac import compare_digest

from universal_bot.domain.entity.common import Entity
from universal_bot.domain.enum.login_attempt.status import LoginAttemptStatus
from universal_bot.domain.exception.auth import LoginCancelledError, LoginRequiredError
from universal_bot.domain.exception.login_attempt import (
    LoginAttemptExpiredError,
    LoginAttemptOwnerMismatchError,
)
from universal_bot.domain.value_object.auth.code_challenge import CodeChallenge
from universal_bot.domain.value_object.auth.device_name import DeviceName
from universal_bot.domain.value_object.auth.installation_id import InstallationId
from universal_bot.domain.value_object.auth.login_code import LoginCode
from universal_bot.domain.value_object.login_attempt.id import LoginAttemptId
from universal_bot.domain.value_object.time.timestamp import Timestamp
from universal_bot.domain.value_object.user.id import TelegramUserId


class LoginAttempt(Entity[LoginAttemptId]):
    _id: LoginAttemptId
    challenge: CodeChallenge
    login_code: LoginCode
    installation_id: InstallationId
    device_name: DeviceName
    expires_at: Timestamp
    status: LoginAttemptStatus
    candidate_id: TelegramUserId | None
    user_id: TelegramUserId | None
    consumed_at: Timestamp | None

    def __init__(
        self,
        *,
        id_: LoginAttemptId,
        challenge: CodeChallenge,
        login_code: LoginCode,
        installation_id: InstallationId,
        device_name: DeviceName,
        expires_at: Timestamp,
        status: LoginAttemptStatus = LoginAttemptStatus.PENDING,
        candidate_id: TelegramUserId | None = None,
        user_id: TelegramUserId | None = None,
        consumed_at: Timestamp | None = None,
    ) -> None:
        super().__init__(id_=id_)
        self.challenge = challenge
        self.login_code = login_code
        self.installation_id = installation_id
        self.device_name = device_name
        self.expires_at = expires_at
        self._status = status
        self.candidate_id = candidate_id
        self.user_id = user_id
        self.consumed_at = consumed_at

    @property
    def status(self) -> LoginAttemptStatus:
        return self._status

    def require_current(self, at: Timestamp) -> None:
        if self.expires_at.value <= at.value or self.consumed_at is not None:
            raise LoginAttemptExpiredError()

    def bind(self, user_id: TelegramUserId, at: Timestamp) -> None:
        self.require_current(at)
        if self.status is not LoginAttemptStatus.PENDING:
            raise LoginAttemptExpiredError()
        if self.candidate_id is not None and self.candidate_id != user_id:
            raise LoginAttemptOwnerMismatchError()
        self.candidate_id = user_id

    def confirm(self, user_id: TelegramUserId, allowed: bool, at: Timestamp) -> None:
        self.bind(user_id, at)
        self.user_id = user_id
        self._status = (
            LoginAttemptStatus.READY if allowed else LoginAttemptStatus.DENIED
        )

    def cancel(self, user_id: TelegramUserId, at: Timestamp) -> None:
        self.bind(user_id, at)
        self._status = LoginAttemptStatus.CANCELLED

    def require_proof(self, challenge: CodeChallenge, at: Timestamp) -> None:
        self.require_current(at)
        if not compare_digest(self.challenge.value, challenge.value):
            raise LoginAttemptOwnerMismatchError()

    def confirmed_user(self, at: Timestamp) -> TelegramUserId:
        self.require_current(at)
        if (
            self.status not in (LoginAttemptStatus.READY, LoginAttemptStatus.DENIED)
            or self.user_id is None
        ):
            raise LoginRequiredError("Подтвердите аккаунт в боте")
        return self.user_id

    def consume(self, at: Timestamp) -> None:
        self.require_current(at)
        if self.status is not LoginAttemptStatus.READY:
            raise LoginCancelledError("Вход не подтверждён")
        self.consumed_at = at
