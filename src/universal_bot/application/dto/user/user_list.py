from pydantic import BaseModel, Field, model_validator

from universal_bot.application.dto.user.user import UserDocumentDTO
from universal_bot.domain.enum.user.role import UserRole


class GetUserListRequestDTO(BaseModel):
    user_id: int
    limit: int = Field(default=20, ge=1, le=100)
    after_id: int | None = None
    role: UserRole | None = None
    gt: bool = False
    lt: bool = False

    @model_validator(mode="after")
    def validate_role_direction(self) -> GetUserListRequestDTO:
        if self.gt and self.lt:
            raise ValueError("Only one of 'gt' or 'lt' can be set at a time")
        return self


class GetUserListResponseDTO(BaseModel):
    user_list: list[UserDocumentDTO]
    after_id: int | None = None
