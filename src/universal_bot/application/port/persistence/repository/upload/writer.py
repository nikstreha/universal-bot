from abc import ABC, abstractmethod
from collections.abc import Sequence

from universal_bot.domain.entity.upload import Upload
from universal_bot.domain.enum.upload.state import UploadState
from universal_bot.domain.value_object.file.idempotency_key import IdempotencyKey
from universal_bot.domain.value_object.time.timestamp import Timestamp
from universal_bot.domain.value_object.upload.id import UploadId
from universal_bot.domain.value_object.user.id import TelegramUserId


class IUploadWriter(ABC):
    @abstractmethod
    async def find_by_id(self, *, key: UploadId) -> Upload | None: ...

    @abstractmethod
    async def list_by_state_expiring_before(
        self, *, state: UploadState, expires_before: Timestamp
    ) -> list[Upload]: ...

    @abstractmethod
    async def list_by_states(
        self, *, states: Sequence[UploadState]
    ) -> list[Upload]: ...

    @abstractmethod
    async def find_by_owner_id_and_operation_key(
        self, *, owner_id: TelegramUserId, operation_key: IdempotencyKey
    ) -> Upload | None: ...

    @abstractmethod
    async def list_by_states_expiring_after(
        self, *, states: Sequence[UploadState], expires_after: Timestamp
    ) -> list[Upload]: ...

    @abstractmethod
    async def add(self, *, entity: Upload) -> None: ...

    @abstractmethod
    async def list_by_owner_and_states(
        self, *, owner_id: TelegramUserId, states: Sequence[UploadState]
    ) -> list[Upload]: ...
