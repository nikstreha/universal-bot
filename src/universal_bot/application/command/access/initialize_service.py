from universal_bot.application.dto.common.policy import Policy
from universal_bot.application.port.clock import IClock
from universal_bot.application.port.persistence.repository.administrator.writer import (
    IAdministratorWriter,
)
from universal_bot.application.port.persistence.repository.user.writer import (
    IUserWriter,
)
from universal_bot.application.port.persistence.uow import IUnitOfWork
from universal_bot.domain.entity.administrator import Administrator
from universal_bot.domain.entity.user import User
from universal_bot.domain.value_object.time.timestamp import Timestamp
from universal_bot.domain.value_object.user.id import TelegramUserId
from universal_bot.domain.value_object.user.name import UserName


class InitializeServiceInteractor:
    def __init__(
        self,
        *,
        policy: Policy,
        administrator_writer: IAdministratorWriter,
        user_writer: IUserWriter,
        clock: IClock,
        uow: IUnitOfWork,
    ) -> None:
        self._administrator_writer = administrator_writer
        self._user_writer = user_writer
        self._user_id = TelegramUserId(policy.admin_id)
        self._clock = clock
        self._uow = uow

    async def __call__(self) -> None:
        async with self._uow:
            administrator = await self._administrator_writer.get()
            if administrator is not None:
                administrator.require_configuration(self._user_id)
                return
            at = Timestamp(self._clock.now())
            user = await self._user_writer.find_by_id(key=self._user_id)
            if user is None:
                await self._user_writer.add(
                    entity=User(
                        id_=self._user_id,
                        name=UserName("Администратор"),
                        created_at=at,
                        last_seen_at=at,
                    )
                )
            await self._administrator_writer.add(
                administrator=Administrator(user_id=self._user_id, created_at=at)
            )
