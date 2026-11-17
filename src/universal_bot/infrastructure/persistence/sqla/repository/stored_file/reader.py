from sqlalchemy import func, select, tuple_

from universal_bot.application.dto.file.filter import FileFilterDTO
from universal_bot.application.port.persistence.repository.stored_file.reader import (
    IStoredFileReader,
)
from universal_bot.application.query_model.file_date_group import (
    FileDateGroupQueryModel,
)
from universal_bot.application.query_model.stored_file import StoredFileQueryModel
from universal_bot.domain.common.util import convert_to_primitive
from universal_bot.domain.value_object.stored_file.id import StoredFileId
from universal_bot.domain.value_object.user.id import TelegramUserId
from universal_bot.infrastructure.persistence.sqla.table.file import file_table as table
from universal_bot.infrastructure.persistence.sqla.type import ReaderSession


class SQLAStoredFileReader(IStoredFileReader):
    def __init__(self, session: ReaderSession) -> None:
        self._session = session

    async def find_by_id(self, *, key: StoredFileId) -> StoredFileQueryModel | None:
        key_raw = convert_to_primitive(key)
        row = (
            (
                await self._session.execute(
                    select(table).where(table.c.id == key_raw).limit(1)
                )
            )
            .mappings()
            .first()
        )
        return StoredFileQueryModel(**row) if row else None

    @staticmethod
    def _catalog_conditions(owner_id: int, filters: FileFilterDTO) -> list:
        conditions = [table.c.owner_id == owner_id, table.c.state == filters.state]
        if filters.collection:
            kinds = (
                ("photo", "video")
                if filters.collection == "media"
                else ("audio", "other")
            )
            conditions.append(table.c.media_kind.in_(kinds))
        if filters.kind:
            conditions.append(table.c.media_kind == filters.kind)
        if filters.q:
            conditions.append(
                func.instr(func.lower(table.c.original_name), filters.q.lower()) > 0
            )
        if filters.date_from:
            conditions.append(table.c.storage_date >= filters.date_from)
        if filters.date_to:
            conditions.append(table.c.storage_date <= filters.date_to)
        return conditions

    async def get_catalog(
        self,
        *,
        owner_id: TelegramUserId,
        filters: FileFilterDTO,
        cursor: tuple[str, int, str] | None,
        limit: int,
    ) -> list[StoredFileQueryModel]:
        owner_id_raw = convert_to_primitive(owner_id)
        statement = select(table).where(
            *self._catalog_conditions(owner_id_raw, filters)
        )
        if cursor:
            statement = statement.where(
                tuple_(table.c.storage_date, table.c.created_at, table.c.id) < cursor
            )
        statement = statement.order_by(
            table.c.storage_date.desc(), table.c.created_at.desc(), table.c.id.desc()
        ).limit(limit)
        return [
            StoredFileQueryModel(**row)
            for row in (await self._session.execute(statement)).mappings()
        ]

    async def get_date_groups(
        self,
        *,
        owner_id: TelegramUserId,
        filters: FileFilterDTO,
        before_date: str,
        limit: int,
    ) -> list[FileDateGroupQueryModel]:
        owner_id_raw = convert_to_primitive(owner_id)
        statement = select(
            table.c.storage_date,
            func.count().label("file_count"),
            func.sum(table.c.size_bytes).label("size_bytes"),
        ).where(*self._catalog_conditions(owner_id_raw, filters))
        if before_date:
            statement = statement.where(table.c.storage_date < before_date)
        statement = (
            statement.group_by(table.c.storage_date)
            .order_by(table.c.storage_date.desc())
            .limit(limit)
        )
        return [
            FileDateGroupQueryModel(**row)
            for row in (await self._session.execute(statement)).mappings()
        ]

    async def get_volumes(self, *, owner_id: TelegramUserId) -> dict[str, int]:
        owner_id_raw = convert_to_primitive(owner_id)
        statement = (
            select(table.c.state, func.sum(table.c.size_bytes))
            .where(table.c.owner_id == owner_id_raw)
            .group_by(table.c.state)
        )
        return dict((await self._session.execute(statement)).all())
