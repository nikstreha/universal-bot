import json

from universal_bot.application.dto.cache.cache_data import CacheDataDTO
from universal_bot.application.dto.cache.cache_key import CacheKey
from universal_bot.application.dto.user.user import UserDocumentDTO
from universal_bot.application.dto.user.user_list import GetUserListRequestDTO
from universal_bot.application.port.cache.cache_provider import ICacheProvider
from universal_bot.application.port.db.repositories.user.reader import IUserReader


class GetUserListInteractor:
    def __init__(self, user_reader: IUserReader, cache: ICacheProvider) -> None:
        self._user_reader = user_reader
        self._cache = cache

    async def __call__(self, request: GetUserListRequestDTO) -> list[UserDocumentDTO]:
        if not request.after_id:
            request = await self.add_after(request)

        user_resp = await self._user_reader.get_collection(request)

        if user_resp.after_id:
            await self._cache.set(
                cache_data=CacheDataDTO(
                    key=f"{CacheKey.USER_LIST}_{request.user_id}",
                    value=json.dumps(user_resp.after_id),
                    expire=60 * 10,
                )
            )
        else:
            await self._cache.delete(
                key=f"{CacheKey.USER_LIST}_{request.user_id}",
            )

        return user_resp.user_list

    async def add_after(self, request: GetUserListRequestDTO) -> GetUserListRequestDTO:
        after_id = await self._cache.get(
            key=f"{CacheKey.USER_LIST}_{request.user_id}",
        )
        if after_id:
            request.after_id = int(after_id)
        return request
