from datetime import datetime

from pydantic import BaseModel, Field

from universal_bot.domain.enum.user.role import UserRole


class UserDocument(BaseModel):
    id_: int = Field(alias="_id")
    role: UserRole
    touched_at: datetime
    user_name: str | None = None
