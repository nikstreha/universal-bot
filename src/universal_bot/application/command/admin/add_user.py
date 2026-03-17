from universal_bot.application.dto.cache.cache_data import CacheDataDTO
from universal_bot.application.dto.cache.cache_key import CacheKey
from universal_bot.application.dto.user.user import AddUserDTO, CacheUserDTO
from universal_bot.application.port.cache.cache_provider import ICacheProvider
from universal_bot.application.port.db.repositories.user.writer import IUserWriter
from universal_bot.domain.entity.user import User
from universal_bot.domain.enum.user.role import UserRole
from universal_bot.domain.value_object.user.id import UserId
from universal_bot.domain.value_object.user.username import UserName


class AddUserInteractor:
    def __init__(
        self,
        user_writer: IUserWriter,
        cache_provider: ICacheProvider,
    ):
        self._user_writer = user_writer
        self._cache_provider = cache_provider

    async def __call__(self, user_dto: AddUserDTO) -> None:
        db_role = UserRole.BANNED if user_dto.role.is_temp() else user_dto.role

        user_entity = User.create(
            id_=UserId(value=user_dto.user_id),
            role=db_role,
            username=UserName(value=user_dto.user_name) if user_dto.user_name else None,
        )

        await self._user_writer.create(user=user_entity)

        if user_dto.role.is_temp():
            cache_user = CacheUserDTO(
                user_id=user_dto.user_id,
                role=user_dto.role,
                user_name=user_dto.user_name,
                expire=user_dto.expire if user_dto.expire else 60 * 60 * 24 * 10,
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
