from abc import ABC, abstractmethod

from universal_bot.domain.entity.upload_part import UploadPart
from universal_bot.domain.value_object.upload.id import UploadId
from universal_bot.domain.value_object.upload.part_id import UploadPartId


class IUploadPartWriter(ABC):
    @abstractmethod
    async def list_by_upload_id(self, *, upload_id: UploadId) -> list[UploadPart]: ...

    @abstractmethod
    async def find_by_id(self, *, key: UploadPartId) -> UploadPart | None: ...

    @abstractmethod
    async def delete(self, *, entity: UploadPart) -> None: ...

    @abstractmethod
    async def add(self, *, entity: UploadPart) -> None: ...
