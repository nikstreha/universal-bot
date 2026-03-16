
from datetime import datetime

from pydantic import BaseModel, Field

from backend_component.domain.enum.user.role import UserRole


class UserDocument(BaseModel):
    id_: str = Field(alias="_id")
    role: UserRole
    touched_at: datetime
    user_name: str