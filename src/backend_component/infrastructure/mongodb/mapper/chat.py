from backend_component.domain.entity.chat import MyChat
from backend_component.infrastructure.mongodb.mapper.message import MessageMapper
from backend_component.infrastructure.mongodb.models.chat import ChatDocument


class ChatMapper:
    @staticmethod
    def to_document(chat: MyChat) -> ChatDocument:
        return ChatDocument(
            id_=chat.id.value,
            user_id=chat.user_id.value,
            messages=[MessageMapper.to_document(msg) for msg in chat.messages],
            created_at=chat.created_at,
            updated_at=chat.updated_at,
        )