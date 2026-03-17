from universal_bot.application.dto.cache.cache_data import CacheDataDTO
from universal_bot.application.dto.cache.cache_key import CacheKey
from universal_bot.application.dto.user.user import CacheUserDTO, UpdateUserRoleDTO
from universal_bot.application.port.cache.cache_provider import ICacheProvider
from universal_bot.application.port.db.repositories.user.writer import IUserWriter
from universal_bot.domain.value_object.user.id import UserId


class UpdateRoleInteractor:
    def __init__(
        self,
        user_writer: IUserWriter,
        cache_provider: ICacheProvider,
    ):
        self._user_writer = user_writer
        self._cache_provider = cache_provider

    async def __call__(self, user_dto: UpdateUserRoleDTO) -> None:
        user_id = UserId(value=user_dto.user_id)
        user = await self._user_writer.get_by_id(user_id=user_id)

        if not user:
            raise

        if not user_dto.role.is_temp():
            await self._user_writer.update_role(user_id=user_id, new_role=user_dto.role)
            await self._cache_provider.delete(
                f"{CacheKey.USER_PERMISSION}:{user_dto.user_id}"
            )
            return

        cache_user = CacheUserDTO(
            user_id=user_dto.user_id,
            role=user_dto.role,
            user_name=user.username.value if user.username else None,
            expire=user_dto.expire or (60 * 60 * 24 * 10),
        )
        await self._cache_user_permissions(cache_user)

    async def _cache_user_permissions(self, user: CacheUserDTO) -> None:
        value = user.model_dump_json()

        await self._cache_provider.set(
            cache_data=CacheDataDTO(
                key=f"{CacheKey.USER_PERMISSION}:{user.user_id}",
                value=value,
                expire=user.expire,
            )
        )
