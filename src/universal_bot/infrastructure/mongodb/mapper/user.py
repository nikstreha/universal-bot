from universal_bot.domain.entity.user import User
from universal_bot.domain.enum.user.role import UserRole
from universal_bot.domain.value_object.user.id import UserId
from universal_bot.domain.value_object.user.username import UserName
from universal_bot.infrastructure.mongodb.documents.user import UserDocument


class UserMapper:
    @staticmethod
    def to_document(user: User) -> UserDocument:
        return UserDocument(
            id_=user.id_.value,
            role=user.role.value,
            touched_at=user.touched_at,
            user_name=user.username.value,
        )

    @staticmethod
    def to_entity(doc: UserDocument) -> User:
        return User(
            id_=UserId(doc.id_),
            role=UserRole(doc.role),
            touched_at=doc.touched_at,
            username=UserName(doc.user_name),
        )
