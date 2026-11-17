from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class AsrConfiguration(BaseModel):
    model_config = ConfigDict(frozen=True)
    model: str = "small"
    device: Literal["cpu", "cuda"] = "cuda"
    compute_type: str = "int8_float16"
    temporary_directory: Path = Path("var/temporary")
    max_audio_seconds: int = Field(default=7200, gt=0)
