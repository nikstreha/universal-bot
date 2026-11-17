from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, field_validator


class FileStorageConfiguration(BaseModel):
    model_config = ConfigDict(frozen=True)
    endpoint: str = "127.0.0.1:9000"
    user: str = "storage-dev"
    password: str = Field(default="storage-dev-password", repr=False)
    bucket: str = "storage-dev"
    secure: bool = False
    disk_path: Path | None = None
    require_mount: bool = False
    min_free_bytes: int = Field(default=1024**3, ge=0)

    @field_validator("disk_path", mode="before")
    @classmethod
    def blank_disk_path(cls, value):
        return None if value == "" else value
