from universal_bot.presentation.http.public_api.common.schema import ResponseModel


class StorageLimitsResponse(ResponseModel):
    max_file_bytes: int
    upload_part_bytes: int
    max_open_uploads: int
    upload_idle_ttl_seconds: int
    trash_retention_days: int


class UserResponse(ResponseModel):
    id: str
    name: str
    is_admin: bool
    volumes: dict[str, int]
    archive_date: str
    archive_timezone: str
    limits: StorageLimitsResponse
