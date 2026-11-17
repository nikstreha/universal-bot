from abc import ABC, abstractmethod

from universal_bot.application.dto.file.filter import FileFilterDTO
from universal_bot.application.query_model.file_date_group import (
    FileDateGroupQueryModel,
)
from universal_bot.application.query_model.stored_file import StoredFileQueryModel
from universal_bot.domain.value_object.stored_file.id import StoredFileId
from universal_bot.domain.value_object.user.id import TelegramUserId


class IStoredFileReader(ABC):
    @abstractmethod
    async def find_by_id(self, *, key: StoredFileId) -> StoredFileQueryModel | None: ...

    @abstractmethod
    async def get_catalog(
        self,
        *,
        owner_id: TelegramUserId,
        filters: FileFilterDTO,
        cursor: tuple[str, int, str] | None,
        limit: int,
    ) -> list[StoredFileQueryModel]: ...

    @abstractmethod
    async def get_date_groups(
        self,
        *,
        owner_id: TelegramUserId,
        filters: FileFilterDTO,
        before_date: str,
        limit: int,
    ) -> list[FileDateGroupQueryModel]: ...

    @abstractmethod
    async def get_volumes(self, *, owner_id: TelegramUserId) -> dict[str, int]: ...
