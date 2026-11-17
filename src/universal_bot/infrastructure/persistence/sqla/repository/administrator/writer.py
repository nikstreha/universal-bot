from sqlalchemy import select

from universal_bot.application.port.persistence.repository.administrator.writer import (
    IAdministratorWriter,
)
from universal_bot.domain.entity.administrator import Administrator
from universal_bot.infrastructure.persistence.sqla.table.administrator import (
    administrator_table,
)
from universal_bot.infrastructure.persistence.sqla.type import WriterSession


class SQLAAdministratorWriter(IAdministratorWriter):
    def __init__(self, session: WriterSession) -> None:
        self._session = session

    async def get(self) -> Administrator | None:
        return await self._session.scalar(
            select(Administrator).where(administrator_table.c.id == 1)
        )

    async def add(self, *, administrator: Administrator) -> None:
        self._session.add(administrator)
        await self._session.flush()
