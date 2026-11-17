from universal_bot.application.port.persistence.repository.user.writer import (
    IUserWriter,
)
from universal_bot.domain.common.util import convert_to_primitive
from universal_bot.domain.entity.user import User
from universal_bot.domain.value_object.user.id import TelegramUserId
from universal_bot.infrastructure.persistence.sqla.type import WriterSession


class SQLAUserWriter(IUserWriter):
    def __init__(self, session: WriterSession) -> None:
        self._session = session

    async def find_by_id(self, *, key: TelegramUserId) -> User | None:
        key_raw = convert_to_primitive(key)
        return await self._session.get(User, key_raw)

    async def add(self, *, entity: User) -> None:
        self._session.add(entity)
        await self._session.flush()
