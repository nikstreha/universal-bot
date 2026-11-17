from universal_bot.domain.entity.common import Entity
from universal_bot.domain.value_object.file.object_key import ObjectKey
from universal_bot.domain.value_object.file.sha256 import SHA256Digest
from universal_bot.domain.value_object.file.size import FileSize
from universal_bot.domain.value_object.upload.id import UploadId
from universal_bot.domain.value_object.upload.part_id import UploadPartId
from universal_bot.domain.value_object.upload.part_index import PartIndex


class UploadPart(Entity[UploadPartId]):
    _identity_field = None
    upload_id: UploadId
    part_index: PartIndex
    size_bytes: FileSize
    sha256: SHA256Digest
    object_key: ObjectKey

    def __init__(
        self,
        *,
        upload_id: UploadId,
        part_index: PartIndex,
        size_bytes: FileSize,
        sha256: SHA256Digest,
        object_key: ObjectKey,
    ) -> None:
        super().__init__(id_=UploadPartId(upload_id, part_index))
        self.size_bytes = size_bytes
        self.sha256 = sha256
        self.object_key = object_key

    @property
    def upload_id(self) -> UploadId:
        return self.id_.upload_id

    @property
    def part_index(self) -> PartIndex:
        return self.id_.part_index
