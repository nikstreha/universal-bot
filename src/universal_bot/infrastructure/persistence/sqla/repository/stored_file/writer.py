from collections.abc import Sequence

from sqlalchemy import select

from universal_bot.application.port.persistence.repository.stored_file.writer import (
    IStoredFileWriter,
)
from universal_bot.domain.common.util import convert_to_primitive
from universal_bot.domain.entity.stored_file import StoredFile
from universal_bot.domain.enum.file.state import FileState
from universal_bot.domain.value_object.stored_file.id import StoredFileId
from universal_bot.domain.value_object.time.timestamp import Timestamp
from universal_bot.infrastructure.persistence.sqla.table.file import file_table
from universal_bot.infrastructure.persistence.sqla.type import WriterSession


class SQLAStoredFileWriter(IStoredFileWriter):
    def __init__(self, session: WriterSession) -> None:
        self._session = session

    async def add(self, *, entity: StoredFile) -> None:
        self._session.add(entity)
        await self._session.flush()

    async def find_by_id(self, *, key: StoredFileId) -> StoredFile | None:
        key_raw = convert_to_primitive(key)
        return await self._session.get(StoredFile, key_raw)

    async def list_due_for_purge(
        self, *, states: Sequence[FileState], purge_before: Timestamp
    ) -> list[StoredFile]:
        states_raw = convert_to_primitive(states)
        purge_before_raw = convert_to_primitive(purge_before)
        statement = select(StoredFile)
        statement = statement.where(
            file_table.c.state.in_(states_raw),
            file_table.c.purge_after < purge_before_raw,
        )
        return list(await self._session.scalars(statement))

    async def delete(self, *, entity: StoredFile) -> None:
        await self._session.delete(entity)
