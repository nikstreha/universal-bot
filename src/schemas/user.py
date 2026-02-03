from pydantic import BaseModel, Field

from src.schemas.user_roles import UserRoles


class UserBaseSchema(BaseModel):
    user_id: int
    role: UserRoles
    username: str = Field(..., max_length=100)
