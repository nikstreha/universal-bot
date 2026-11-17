from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class StoredFileQueryModel:
    id: str
    owner_id: int
    upload_id: str
    object_key: str
    original_name: str
    size_bytes: int
    sha256: str
    storage_date: str
    storage_timezone: str
    mime_type: str
    media_kind: str
    created_at: int
    checked_at: int
    state: str = "active"
    trashed_at: int | None = None
    purge_after: int | None = None
    integrity: str = "verified"
    thumbnail_key: str | None = None
    thumbnail_state: str = "pending"
