import re
from typing import Literal
from urllib.parse import urlsplit

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class TelegramConfiguration(BaseModel):
    model_config = ConfigDict(frozen=True)
    token: str = Field(default="", repr=False)
    username: str = ""
    mode: Literal["polling", "webhook"] = "polling"
    public_url: str = "http://localhost:7000"
    webhook_secret: str = Field(default="", repr=False)

    @field_validator("webhook_secret")
    @classmethod
    def valid_webhook_secret(cls, value: str) -> str:
        if value and re.fullmatch(r"[A-Za-z0-9_-]{32,256}", value) is None:
            raise ValueError("Webhook secret must contain 32–256 URL-safe characters")
        return value

    @model_validator(mode="after")
    def validate_transport(self) -> TelegramConfiguration:
        if self.mode == "webhook":
            _ = self.webhook_url
        return self

    @property
    def webhook_url(self) -> str:
        origin = urlsplit(self.public_url)
        if (
            origin.scheme != "https"
            or not origin.hostname
            or origin.username
            or origin.password
            or origin.query
            or origin.fragment
            or origin.path not in ("", "/")
        ):
            raise ValueError("APP__TELEGRAM__PUBLIC_URL must be an HTTPS origin")
        if not self.webhook_secret:
            raise ValueError("APP__TELEGRAM__WEBHOOK_SECRET is required")
        return self.public_url.rstrip("/") + "/telegram/webhook"
