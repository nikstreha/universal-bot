from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class StorageLimitsQueryModel:
    max_file_bytes: int
    upload_part_bytes: int
    max_open_uploads: int
    upload_idle_ttl_seconds: int
    trash_retention_days: int


@dataclass(frozen=True, slots=True, kw_only=True)
class ProfileQueryModel:
    id: str
    name: str
    is_admin: bool
    volumes: dict[str, int]
    archive_date: str
    archive_timezone: str
    limits: StorageLimitsQueryModel
