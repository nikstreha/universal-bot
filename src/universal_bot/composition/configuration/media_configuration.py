from pathlib import Path

from pydantic import BaseModel, ConfigDict


class MediaConfiguration(BaseModel):
    model_config = ConfigDict(frozen=True)
    temporary_directory: Path = Path("var/temporary")
