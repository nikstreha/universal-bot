from pymongo.asynchronous.database import AsyncDatabase

from backend_component.domain.entity.user import User
from backend_component.domain.enum.user.role import UserRole
from backend_component.infrastructure.mongodb.collections import Collections
from backend_component.infrastructure.mongodb.mapper.user import UserMapper


class UserWriter:
    def __init__(self, db: AsyncDatabase) -> None:
        self.collection = db[Collections.USER]

    async def replace(self, user: User) -> None:
        doc = UserMapper.to_document(user).model_dump()

        await self.collection.replace_one(
            {"_id": doc["_id"]},
            doc,
        )
    
    async def update_role(
        self,
        user: User,
        new_role: UserRole,
    ) -> None:
        user.change_role(new_role)

        await self.replace(user)

    async def create(self, user: User) -> None:
        doc = UserMapper.to_document(user).model_dump()

        await self.collection.insert_one(doc)
