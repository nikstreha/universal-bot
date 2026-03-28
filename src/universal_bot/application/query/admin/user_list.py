from universal_bot.application.dto.user.user import (
    GetUserListRequestDTO,
    UserDocumentDTO,
)
from universal_bot.application.port.db.repositories.user.reader import IUserReader


class GetUserListQuery:
    def __init__(self, user_reader: IUserReader) -> None:
        self._user_reader = user_reader

    async def __call__(self, request: GetUserListRequestDTO) -> list[UserDocumentDTO]:
        return await self._user_reader.get_collection(request)
