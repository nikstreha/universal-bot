from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class CreateUploadRequestDTO:
    user_id: int
    operation_key: str
    original_name: str
    size_bytes: int
    sha256: str
    declared_mime: str = "application/octet-stream"
