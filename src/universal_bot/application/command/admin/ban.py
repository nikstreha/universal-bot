from universal_bot.application.exeption.user import UserNotFoundError
from universal_bot.application.port.db.repositories.user.writer import IUserWriter
from universal_bot.domain.value_object.user.id import UserId


class BanUserInteractor:
    def __init__(self, user_writer: IUserWriter):
        self._user_writer = user_writer

    async def __call__(self, user_id: int) -> None:
        id_ = UserId(user_id)
        user = await self._user_writer.get_by_id(user_id=id_)
        if not user:
            raise UserNotFoundError(f"User {user_id} not found")
        await self._user_writer.ban(id_)
