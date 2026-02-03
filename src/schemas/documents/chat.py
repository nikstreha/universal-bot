from beanie import Document

from src.schemas.db_chat import DBHistorySchema
from src.schemas.user import UserBaseSchema

class Chat(Document):
    user: UserBaseSchema
    history: DBHistorySchema | None = None
