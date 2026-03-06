from pymongo.asynchronous.database import AsyncDatabase

from backend_component.domain.entity.user import User
from backend_component.domain.enum.user.role import UserRole
from backend_component.domain.value_object.user.id import UserId
from backend_component.infrastructure.mongodb.collections import Collections
from backend_component.infrastructure.mongodb.mapper.user import UserMapper


class UserWriter:
    def __init__(self, db: AsyncDatabase) -> None:
        self.collection = db[Collections.USER]

    async def get_by_id(self, user_id: UserId) -> User | None:
        doc = await self.collection.find_one({"_id": user_id})

        if not doc:
            return None

        return UserMapper.to_entity(doc)

    async def replace(self, user: User) -> None:
        doc = UserMapper.to_document(user).model_dump()

        await self.collection.replace_one(
            {"_id": doc["_id"]},
            doc,
        )
    
    async def update_role(
        self,
        user_id: UserId,
        new_role: UserRole,
    ) -> None:
        user = await self.get_by_id(user_id)

        if not user:
            raise ValueError(f"User with id {user_id} not found")
        
        user.change_role(new_role)

        await self.replace(user)

    async def create(self, user: User) -> None:
        doc = UserMapper.to_document(user).model_dump()

        await self.collection.insert_one(doc)

    async def ban(self, user_id: UserId) -> None:
        await self.update_role(user_id=user_id, new_role=UserRole.BANNED)
