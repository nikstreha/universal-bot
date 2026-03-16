from abc import ABC, abstractmethod

from universal_bot.domain.entity.user import User
from universal_bot.domain.enum.user.role import UserRole
from universal_bot.domain.value_object.user.id import UserId


class IUserWriter(ABC):
    @abstractmethod
    async def get_by_id(self, user_id: UserId) -> User | None: ...

    @abstractmethod
    async def replace(self, user: User) -> None: ...

    @abstractmethod
    async def update_role(self, user_id: UserId, new_role: UserRole) -> None: ...

    @abstractmethod
    async def create(self, user: User) -> None: ...

    @abstractmethod
    async def ban(self, user_id: UserId) -> None: ...
