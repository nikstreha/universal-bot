from zoneinfo import ZoneInfo

from pydantic import BaseModel, ConfigDict, Field, field_validator


class StorageConfiguration(BaseModel):
    model_config = ConfigDict(frozen=True)
    archive_timezone: str = "Europe/Minsk"
    max_file_bytes: int = Field(default=10 * 1024**3, ge=0)
    part_bytes: int = Field(default=8 * 1024**2, ge=5 * 1024**2, le=32 * 1024**2)
    max_open_uploads: int = Field(default=10, gt=0)
    upload_idle_seconds: int = Field(default=7 * 86400, gt=0)
    trash_retention_days: int = Field(default=30, gt=0)

    @field_validator("archive_timezone")
    @classmethod
    def valid_timezone(cls, value: str) -> str:
        ZoneInfo(value)
        return value
