from universal_bot.application.exception.common import AuthAttemptExpiredError
from universal_bot.application.port.clock import IClock
from universal_bot.application.port.persistence.repository.login_attempt.writer import (
    ILoginAttemptWriter,
)
from universal_bot.application.port.persistence.uow import IUnitOfWork
from universal_bot.application.port.security.secrets import ISecrets
from universal_bot.domain.common.guard import ensure
from universal_bot.domain.enum.login_attempt.status import LoginAttemptStatus
from universal_bot.domain.exception.auth import LoginRequiredError
from universal_bot.domain.value_object.auth.code_challenge import CodeChallenge
from universal_bot.domain.value_object.login_attempt.id import LoginAttemptId
from universal_bot.domain.value_object.time.timestamp import Timestamp


class GetDeniedLoginIdentityInteractor:
    def __init__(
        self,
        *,
        uow: IUnitOfWork,
        clock: IClock,
        login_attempt_writer: ILoginAttemptWriter,
        secrets: ISecrets,
    ) -> None:
        self._uow = uow
        self._clock = clock
        self._login_attempt_writer = login_attempt_writer
        self._secrets = secrets

    async def __call__(self, *, attempt_id: str, verifier: str) -> int:
        async with self._uow:
            attempt = await self._login_attempt_writer.find_by_id(
                key=LoginAttemptId(attempt_id)
            )
            ensure(attempt, AuthAttemptExpiredError, "Войдите через Telegram ещё раз")
            attempt.require_proof(
                CodeChallenge(self._secrets.challenge(verifier)),
                Timestamp(self._clock.now()),
            )
            ensure(
                attempt.status is LoginAttemptStatus.DENIED,
                LoginRequiredError,
                "Подтвердите аккаунт в боте",
            )
            return attempt.confirmed_user(Timestamp(self._clock.now())).value
