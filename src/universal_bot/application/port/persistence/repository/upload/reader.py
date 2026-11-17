from abc import ABC, abstractmethod

from universal_bot.application.query_model.upload import UploadQueryModel
from universal_bot.domain.value_object.upload.id import UploadId


class IUploadReader(ABC):
    @abstractmethod
    async def find_by_id(self, *, key: UploadId) -> UploadQueryModel | None: ...
