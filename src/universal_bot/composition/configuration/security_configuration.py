from pydantic import BaseModel, ConfigDict, Field, model_validator


class SecurityConfiguration(BaseModel):
    model_config = ConfigDict(frozen=True)
    admin_id: int = Field(gt=0, lt=2**63)
    session_idle_seconds: int = Field(default=30 * 86400, gt=0)
    session_max_seconds: int = Field(default=90 * 86400, gt=0)

    @model_validator(mode="after")
    def valid_session_lifetime(self) -> SecurityConfiguration:
        if self.session_idle_seconds > self.session_max_seconds:
            raise ValueError(
                "Session idle lifetime must not exceed its maximum lifetime"
            )
        return self
