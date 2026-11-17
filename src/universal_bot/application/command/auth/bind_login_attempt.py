from universal_bot.application.port.clock import IClock
from universal_bot.application.port.persistence.repository.login_attempt.writer import (
    ILoginAttemptWriter,
)
from universal_bot.application.port.persistence.uow import IUnitOfWork
from universal_bot.domain.common.guard import ensure
from universal_bot.domain.entity.login_attempt import LoginAttempt
from universal_bot.domain.exception.common import NotFoundError
from universal_bot.domain.value_object.login_attempt.id import LoginAttemptId
from universal_bot.domain.value_object.time.timestamp import Timestamp
from universal_bot.domain.value_object.user.id import TelegramUserId


class BindLoginAttemptInteractor:
    def __init__(
        self,
        *,
        clock: IClock,
        login_attempt_writer: ILoginAttemptWriter,
        uow: IUnitOfWork,
    ) -> None:
        self._clock = clock
        self._login_attempt_writer = login_attempt_writer
        self._uow = uow

    async def __call__(self, *, attempt_id: str, user_id: int) -> LoginAttempt:
        async with self._uow:
            attempt = await self._login_attempt_writer.find_by_id(
                key=LoginAttemptId(attempt_id)
            )
            ensure(attempt, NotFoundError, "Попытка входа не найдена")
            attempt.bind(TelegramUserId(user_id), Timestamp(self._clock.now()))
            return attempt
