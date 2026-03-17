from pydantic import BaseModel

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
