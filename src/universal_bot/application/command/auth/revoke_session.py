from universal_bot.application.port.clock import IClock
from universal_bot.application.port.persistence.repository.session.writer import (
    ISessionWriter,
)
from universal_bot.application.port.persistence.uow import IUnitOfWork
from universal_bot.domain.common.guard import ensure
from universal_bot.domain.exception.common import NotFoundError
from universal_bot.domain.value_object.session.id import SessionId
from universal_bot.domain.value_object.time.timestamp import Timestamp


class RevokeSessionInteractor:
    def __init__(
        self, *, clock: IClock, session_writer: ISessionWriter, uow: IUnitOfWork
    ) -> None:
        self._clock = clock
        self._session_writer = session_writer
        self._uow = uow

    async def __call__(self, *, user_id: int, session_id: str) -> None:
        async with self._uow:
            session = await self._session_writer.find_by_id(key=SessionId(session_id))
            ensure(
                session and session.user_id.value == user_id,
                NotFoundError,
                "Сессия не найдена",
            )
            session.revoke(Timestamp(self._clock.now()))
