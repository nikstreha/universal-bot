from sqlalchemy import func, or_, select

from universal_bot.application.port.persistence.repository.user.reader import (
    IUserReader,
)
from universal_bot.application.query_model.user import (
    AdminUserQueryModel,
    UserQueryModel,
)
from universal_bot.domain.common.util import convert_to_primitive
from universal_bot.domain.value_object.user.id import TelegramUserId
from universal_bot.infrastructure.persistence.sqla.table.file import file_table
from universal_bot.infrastructure.persistence.sqla.table.user import user_table as table
from universal_bot.infrastructure.persistence.sqla.table.whitelist import (
    whitelist_table,
)
from universal_bot.infrastructure.persistence.sqla.type import ReaderSession


class SQLAUserReader(IUserReader):
    def __init__(self, session: ReaderSession) -> None:
        self._session = session

    async def find_by_id(self, *, key: TelegramUserId) -> UserQueryModel | None:
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
        return UserQueryModel(**row) if row else None

    async def get_whitelisted_with_usage(
        self, *, admin_id: TelegramUserId
    ) -> list[AdminUserQueryModel]:
        admin_id_raw = convert_to_primitive(admin_id)
        statement = (
            select(
                table.c.id,
                table.c.name,
                func.count(file_table.c.id).label("files"),
                func.coalesce(func.sum(file_table.c.size_bytes), 0).label("bytes"),
            )
            .select_from(
                table.outerjoin(
                    whitelist_table, whitelist_table.c.user_id == table.c.id
                ).outerjoin(file_table, file_table.c.owner_id == table.c.id)
            )
            .where(
                or_(table.c.id == admin_id_raw, whitelist_table.c.user_id.is_not(None))
            )
            .group_by(table.c.id, table.c.name)
            .order_by(table.c.id)
        )
        return [
            AdminUserQueryModel(**row)
            for row in (await self._session.execute(statement)).mappings()
        ]
