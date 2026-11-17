from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class UploadPartQueryModel:
    upload_id: str
    part_index: int
    size_bytes: int
    sha256: str
    object_key: str
