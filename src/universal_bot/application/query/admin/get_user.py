from universal_bot.application.dto.user.user import UserDocumentDTO
from universal_bot.application.port.db.repositories.user.reader import IUserReader


class GetUserInteractor:
    def __init__(self, user_reader: IUserReader) -> None:
        self._user_reader = user_reader

    async def __call__(self, user_id: int) -> UserDocumentDTO | None:
        return await self._user_reader.get_by_id(user_id)
