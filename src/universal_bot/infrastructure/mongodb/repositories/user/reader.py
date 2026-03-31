from pymongo.asynchronous.database import AsyncDatabase

from universal_bot.application.dto.user.user import UserDocumentDTO
from universal_bot.application.dto.user.user_list import (
    GetUserListRequestDTO,
    GetUserListResponseDTO,
)
from universal_bot.application.port.db.repositories.user.reader import (
    IUserReader,
)
from universal_bot.domain.enum.user.role import UserRole
from universal_bot.infrastructure.mongodb.collections import Collections


class UserReader(IUserReader):
    def __init__(self, db: AsyncDatabase) -> None:
        self.collection = db[Collections.USER]

    async def get_by_id(self, user_id: int) -> UserDocumentDTO | None:
        doc = await self.collection.find_one({"_id": user_id})

        if not doc:
            return None

        return UserDocumentDTO.model_validate(doc)

    async def is_user_permitted(self, user_id: int) -> bool:
        doc = await self.collection.find_one({"_id": user_id})

        if doc:
            return UserDocumentDTO(**doc).role.is_permitted()

        return False

    async def is_user_admin(self, user_id: int) -> bool:
        doc = await self.collection.find_one({"_id": user_id})

        if doc:
            return UserDocumentDTO(**doc).role.is_admin()

        return False

    async def get_collection(
        self, request: GetUserListRequestDTO
    ) -> GetUserListResponseDTO:
        query: dict = {}

        if request.after_id:
            query["_id"] = {"$gt": request.after_id}

        if request.role:
            if request.gt:
                matching_roles = [r for r in UserRole if r > request.role]
            elif request.lt:
                matching_roles = [r for r in UserRole if r < request.role]
            else:
                matching_roles = [request.role]
            query["role"] = {"$in": [r.value for r in matching_roles]}

        docs = (
            await self.collection.find(query)
            .sort("_id", 1)
            .limit(request.limit + 1)
            .to_list(length=request.limit + 1)
        )

        if len(docs) > request.limit:
            after_id = docs[-1]["_id"]
            docs.pop()
        else:
            after_id = None

        response = GetUserListResponseDTO(
            user_list=[UserDocumentDTO.model_validate(doc) for doc in docs],
            after_id=after_id,
        )

        return response
