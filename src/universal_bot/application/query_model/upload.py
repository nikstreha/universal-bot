from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class UploadQueryModel:
    id: str
    owner_id: int
    operation_key: str
    original_name: str
    size_bytes: int
    sha256: str
    declared_mime: str
    storage_date: str
    storage_timezone: str
    part_bytes: int
    created_at: int
    expires_at: int
    state: str = "receiving"
    file_id: str | None = None
    error: str | None = None

    @property
    def part_count(self) -> int:
        return (self.size_bytes + self.part_bytes - 1) // self.part_bytes
