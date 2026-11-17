from abc import ABC, abstractmethod
from collections.abc import Sequence

from universal_bot.domain.entity.stored_file import StoredFile
from universal_bot.domain.enum.file.state import FileState
from universal_bot.domain.value_object.stored_file.id import StoredFileId
from universal_bot.domain.value_object.time.timestamp import Timestamp


class IStoredFileWriter(ABC):
    @abstractmethod
    async def add(self, *, entity: StoredFile) -> None: ...

    @abstractmethod
    async def find_by_id(self, *, key: StoredFileId) -> StoredFile | None: ...

    @abstractmethod
    async def list_due_for_purge(
        self, *, states: Sequence[FileState], purge_before: Timestamp
    ) -> list[StoredFile]: ...

    @abstractmethod
    async def delete(self, *, entity: StoredFile) -> None: ...
