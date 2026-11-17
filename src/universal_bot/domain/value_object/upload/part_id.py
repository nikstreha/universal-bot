from dataclasses import dataclass

from universal_bot.domain.value_object.common import ValueObject
from universal_bot.domain.value_object.upload.id import UploadId
from universal_bot.domain.value_object.upload.part_index import PartIndex


@dataclass(frozen=True, slots=True, repr=False)
class UploadPartId(ValueObject):
    upload_id: UploadId
    part_index: PartIndex

    def __post_init__(self) -> None:
        object.__setattr__(self, "upload_id", UploadId.from_raw(self.upload_id))
        object.__setattr__(self, "part_index", PartIndex.from_raw(self.part_index))

    @classmethod
    def from_raw(cls, value):
        return value if isinstance(value, cls) else cls(*value)
