from typing import Literal

from pydantic import BaseModel, ConfigDict


class ServerConfiguration(BaseModel):
    model_config = ConfigDict(frozen=True)
    env: Literal["dev", "production"] = "dev"
    app_name: str = "storage"
    api_version: str = "0.2.0"
    enable_api_docs: bool = False
