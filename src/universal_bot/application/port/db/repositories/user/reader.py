from abc import ABC, abstractmethod

from universal_bot.application.dto.user.user import (
    GetUserListRequestDTO,
    UserDocumentDTO,
)


class IUserReader(ABC):
    @abstractmethod
    async def get_by_id(self, user_id: int) -> UserDocumentDTO | None: ...

    @abstractmethod
    async def is_user_permitted(self, user_id: int) -> bool: ...

    @abstractmethod
    async def is_user_admin(self, user_id: int) -> bool: ...

    @abstractmethod
    async def get_collection(
        self, request: GetUserListRequestDTO
    ) -> list[UserDocumentDTO]: ...
