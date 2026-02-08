from pydantic import Field
from beanie import Document
from beanie.operators import Push
from src.schemas.user_roles import UserRoles
from src.core.config import settings
from src.schemas.chat import HistorySchema
from src.schemas.db_chat import DBHistorySchema, DBMessageSchema
from src.schemas.user import UserBaseSchema


class Chat(Document):
    user: UserBaseSchema
    history: DBHistorySchema = Field(default_factory=DBHistorySchema)

    def __repr__(self) -> str:
        return f"Chat(user={self.user.user_id}, username={self.user.username})"
    
    @classmethod
    async def update_role(cls, user_id: int, role: UserRoles) -> None:
        await cls.find_one(
            cls.user.user_id == user_id).update({"user.role": role}
            )
        
    @classmethod
    async def ban_user(cls, user_id: int) -> None:
        await cls.update_role(user_id, UserRoles.BANNED)
    
    @classmethod
    async def from_user(cls, user_id: int) -> Chat | None:
        return await cls.find_one(cls.user.user_id == user_id)
    
    @classmethod
    async def get_history(cls, user_id: int, limit: int = 10) -> HistorySchema:
        user_doc = await cls.from_user(user_id)

        if not user_doc:
            return HistorySchema()

        return HistorySchema(messages=user_doc.history.messages[-limit:])
    
    @classmethod
    async def get_user(cls, user_id: int) -> UserBaseSchema | None:
        user_doc: Chat | None = await cls.from_user(user_id)
        return user_doc.user if user_doc else None

    @classmethod
    async def create_for_user(cls, user: UserBaseSchema) -> Chat:
        existing = await cls.from_user(user.user_id)
        if existing:
            return existing

        chat = cls(user=user, history=DBHistorySchema())
        await chat.insert()
        return chat
    
    async def add_message(self, message: DBMessageSchema) -> None:
        await self.update(
            Push(
                {
                    "history.messages": {
                        "$each": [message],
                        "$slice": -settings.MAX_HISTORY,
                        }
                    }
                )
            )
