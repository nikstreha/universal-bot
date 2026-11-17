from abc import ABC, abstractmethod

from universal_bot.application.query_model.upload_part import UploadPartQueryModel
from universal_bot.domain.value_object.upload.id import UploadId


class IUploadPartReader(ABC):
    @abstractmethod
    async def list_by_upload_id(
        self, *, upload_id: UploadId
    ) -> list[UploadPartQueryModel]: ...
