from datetime import datetime

from pydantic import BaseModel, Field, model_validator

from universal_bot.domain.enum.user.role import UserRole


class AddUserDTO(BaseModel):
    user_id: int
    role: UserRole
    user_name: str | None
    expire: int | None = None


class UpdateUserRoleDTO(BaseModel):
    user_id: int
    role: UserRole
    expire: int | None = None


class CacheUserDTO(BaseModel):
    user_id: int
    role: UserRole
    user_name: str | None
    expire: int


class UserDocumentDTO(BaseModel):
    id_: int = Field(alias="_id")
    role: UserRole
    touched_at: datetime
    user_name: str | None = None


class GetUserListRequestDTO(BaseModel):
    limit: int = 20
    after_id: int | None = None
    role: UserRole | None = None
    gt: bool = False
    lt: bool = False

    @model_validator(mode="after")
    def validate_role_direction(self) -> GetUserListRequestDTO:
        if self.gt and self.lt:
            raise ValueError("Only one of 'gt' or 'lt' can be set at a time")
        return self
