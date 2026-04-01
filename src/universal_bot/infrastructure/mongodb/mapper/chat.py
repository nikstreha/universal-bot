from universal_bot.domain.entity.chat import Chat
from universal_bot.domain.value_object.chat.id import ChatId
from universal_bot.domain.value_object.chat.tg_chat_id import TgChatId
from universal_bot.domain.value_object.user.id import UserId
from universal_bot.infrastructure.mongodb.documents.chat import ChatDocument


class ChatMapper:
    @staticmethod
    def to_document(chat: Chat) -> ChatDocument:
        return ChatDocument(
            _id=chat.id_.value,
            tg_chat_id=chat.tg_chat_id.value,
            user_id=chat.user_id.value,
            created_at=chat.created_at,
            updated_at=chat.updated_at,
        )

    @staticmethod
    def to_entity(doc: ChatDocument) -> Chat:
        return Chat(
            id_=ChatId(doc.id_),
            tg_chat_id=TgChatId(doc.tg_chat_id),
            user_id=UserId(doc.user_id),
            created_at=doc.created_at,
            updated_at=doc.updated_at,
        )
