from abc import ABC, abstractmethod

from universal_bot.domain.entity.verification import Verification
from universal_bot.domain.value_object.file.idempotency_key import IdempotencyKey
from universal_bot.domain.value_object.stored_file.id import StoredFileId
from universal_bot.domain.value_object.verification.id import VerificationId


class IVerificationWriter(ABC):
    @abstractmethod
    async def find_by_id(self, *, key: VerificationId) -> Verification | None: ...

    @abstractmethod
    async def list_by_file_id(self, *, file_id: StoredFileId) -> list[Verification]: ...

    @abstractmethod
    async def delete(self, *, entity: Verification) -> None: ...

    @abstractmethod
    async def find_by_file_id_and_operation_key(
        self, *, file_id: StoredFileId, operation_key: IdempotencyKey
    ) -> Verification | None: ...

    @abstractmethod
    async def add(self, *, entity: Verification) -> None: ...
