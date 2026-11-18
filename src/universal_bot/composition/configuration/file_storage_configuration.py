from pathlib import Path
from urllib.parse import urlsplit

from pydantic import BaseModel, ConfigDict, Field, field_validator


class FileStorageConfiguration(BaseModel):
    model_config = ConfigDict(frozen=True)
    endpoint: str = "127.0.0.1:3900"
    user: str = "storage-dev"
    password: str = Field(default="storage-dev-password", repr=False)
    bucket: str = "storage-dev"
    staging_bucket: str = "storage-dev-staging"
    region: str = "garage"
    secure: bool = False
    disk_path: Path | None = None
    require_mount: bool = False
    min_free_bytes: int = Field(default=1024**3, ge=0)

    @property
    def endpoint_url(self) -> str:
        return ("https://" if self.secure else "http://") + self.endpoint.rstrip("/")

    @field_validator("endpoint")
    @classmethod
    def valid_endpoint(cls, value: str) -> str:
        parsed = urlsplit("http://" + value)
        if (
            not parsed.hostname
            or parsed.username
            or parsed.password
            or parsed.query
            or parsed.fragment
            or parsed.path not in ("", "/")
        ):
            raise ValueError(
                "Storage endpoint must be a host with optional port, without URL credentials or path"
            )
        _ = parsed.port
        return value.rstrip("/")

    @field_validator("disk_path", mode="before")
    @classmethod
    def blank_disk_path(cls, value):
        return None if value == "" else value
