from datetime import datetime

from pydantic import BaseModel, Field

from universal_bot.domain.enum.user.role import UserRole


class AddUserDTO(BaseModel):
    user_id: int
    role: UserRole
    user_name: str | None
    expire: int | None = Field(default=None, gt=0)


class UpdateUserRoleDTO(BaseModel):
    user_id: int
    role: UserRole
    expire: int | None = Field(default=None, gt=0)


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


class UserCollectionResponseDTO(BaseModel):
    cursor: int | None = None
    user_list: list[UserDocumentDTO]
