from universal_bot.application.dto.user.user import UserCollectionResponseDTO
from universal_bot.application.dto.user.user_list import GetUserListRequestDTO
from universal_bot.application.port.db.repositories.user.reader import IUserReader


class GetUserListInteractor:
    def __init__(self, user_reader: IUserReader) -> None:
        self._user_reader = user_reader

    async def __call__(
        self, request: GetUserListRequestDTO
    ) -> UserCollectionResponseDTO:
        user_resp = await self._user_reader.get_collection(request)

        cursor = user_resp.after_id

        return UserCollectionResponseDTO(
            user_list=user_resp.user_list,
            cursor=cursor,
        )
