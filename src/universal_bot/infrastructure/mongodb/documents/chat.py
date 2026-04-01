from datetime import datetime

from pydantic import BaseModel, Field


class ChatDocument(BaseModel):
    id_: int = Field(alias="_id")
    tg_chat_id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
