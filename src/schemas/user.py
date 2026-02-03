from enum import Enum

from pydantic import BaseModel, Field


class AdminRoles(str, Enum):
    SUPERADMIN = "superadmin"
    ADMIN = "admin"
    TEMP_ADMIN = "temp_admin"


class UserRoles(AdminRoles):
    USER = "user"
    TEMP_USER = "temp_user"
    OTHER = "other"


class UserBaseSchema(BaseModel):
    user_id: int
    role: UserRoles
    username: str = Field(..., max_length=100)
