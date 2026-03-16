from backend_component.domain.entity.user import User
from backend_component.domain.enum.user.role import UserRole
from backend_component.domain.value_object.user.id import UserId
from backend_component.domain.value_object.user.username import UserName
from backend_component.infrastructure.mongodb.documents.user import UserDocument


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
