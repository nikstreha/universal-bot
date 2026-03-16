from universal_bot.domain.entity.chat import MyChat
from universal_bot.infrastructure.mongodb.documents.chat import ChatDocument
from universal_bot.infrastructure.mongodb.mapper.message import MessageMapper


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
