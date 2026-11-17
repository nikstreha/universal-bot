from types import TracebackType

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from universal_bot.application.port.persistence.uow import IUnitOfWork


class SQLAUnitOfWork(IUnitOfWork):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory
        self._session: AsyncSession | None = None

    @property
    def session(self) -> AsyncSession:
        if self._session is None:
            raise RuntimeError("Writer session requires an active Unit of Work")
        return self._session

    async def __aenter__(self) -> SQLAUnitOfWork:
        if self._session is not None:
            raise RuntimeError("Nested Unit of Work is not supported")
        self._session = self._session_factory()
        try:
            await self._session.execute(text("BEGIN IMMEDIATE"))
        except BaseException:
            await self._session.close()
            self._session = None
            raise
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        session = self.session
        try:
            if exc_type is None:
                await session.commit()
            else:
                await session.rollback()
        except BaseException:
            await session.rollback()
            raise
        finally:
            await session.close()
            self._session = None

    async def flush(self) -> None:
        await self.session.flush()
