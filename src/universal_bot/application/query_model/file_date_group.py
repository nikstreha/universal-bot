from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class FileDateGroupQueryModel:
    storage_date: str
    file_count: int
    size_bytes: int
