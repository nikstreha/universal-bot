from abc import ABC, abstractmethod

from universal_bot.infrastructure.mongodb.documents.user import UserDocument


class IUserReader(ABC):
    @abstractmethod
    async def get_by_id(self, user_id: int) -> UserDocument | None: ...

    @abstractmethod
    async def is_user_permitted(self, user_id: int) -> bool: ...

    @abstractmethod
    async def is_user_admin(self, user_id: int) -> bool: ...
