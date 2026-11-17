from sqlalchemy import select

from universal_bot.application.port.persistence.repository.administrator.reader import (
    IAdministratorReader,
)
from universal_bot.domain.entity.administrator import Administrator
from universal_bot.infrastructure.persistence.sqla.table.administrator import (
    administrator_table,
)
from universal_bot.infrastructure.persistence.sqla.type import ReaderSession


class SQLAAdministratorReader(IAdministratorReader):
    def __init__(self, session: ReaderSession) -> None:
        self._session = session

    async def get(self) -> Administrator | None:
        return await self._session.scalar(
            select(Administrator).where(administrator_table.c.id == 1)
        )
