from universal_bot.application.dto.common.policy import Policy
from universal_bot.application.exception.common import LoginNotConfiguredError
from universal_bot.application.port.clock import IClock
from universal_bot.application.port.persistence.repository.login_attempt.writer import (
    ILoginAttemptWriter,
)
from universal_bot.application.port.persistence.uow import IUnitOfWork
from universal_bot.application.port.security.secrets import ISecrets
from universal_bot.application.query_model.login import LoginAttemptQueryModel
from universal_bot.domain.common.guard import ensure
from universal_bot.domain.entity.login_attempt import LoginAttempt
from universal_bot.domain.exception.common import RateLimitedError
from universal_bot.domain.value_object.auth.code_challenge import CodeChallenge
from universal_bot.domain.value_object.auth.device_name import DeviceName
from universal_bot.domain.value_object.auth.installation_id import InstallationId
from universal_bot.domain.value_object.auth.login_code import LoginCode
from universal_bot.domain.value_object.login_attempt.id import LoginAttemptId
from universal_bot.domain.value_object.time.timestamp import Timestamp


class CreateLoginAttemptInteractor:
    def __init__(
        self,
        *,
        clock: IClock,
        login_attempt_writer: ILoginAttemptWriter,
        policy: Policy,
        secrets: ISecrets,
        uow: IUnitOfWork,
    ) -> None:
        self._clock = clock
        self._login_attempt_writer = login_attempt_writer
        self._policy = policy
        self._secrets = secrets
        self._uow = uow

    async def __call__(
        self, *, challenge: str, installation_id: str, device_name: str
    ) -> LoginAttemptQueryModel:
        ensure(
            self._policy.bot_username,
            LoginNotConfiguredError,
            "Вход через бота ещё не настроен",
        )
        async with self._uow:
            await self._login_attempt_writer.delete_expired(
                at=Timestamp(self._clock.now())
            )
            ensure(
                await self._login_attempt_writer.count_active(
                    at=Timestamp(self._clock.now())
                )
                < 200,
                RateLimitedError,
                "Слишком много попыток входа",
                retry_after=60,
            )
            attempt = LoginAttempt(
                id_=LoginAttemptId(self._secrets.identity()),
                challenge=CodeChallenge(challenge),
                login_code=LoginCode(self._secrets.login_code()),
                installation_id=InstallationId(installation_id),
                device_name=DeviceName(" ".join(device_name.split())[:100]),
                expires_at=Timestamp(self._clock.now() + 300),
            )
            await self._login_attempt_writer.add(entity=attempt)
            return LoginAttemptQueryModel(
                attempt_id=str(attempt.id_.value),
                authorization_url=f"https://t.me/{self._policy.bot_username}?start=login_{attempt.id_.value}",
                login_code=attempt.login_code.value,
                expires_at=attempt.expires_at.value,
            )
