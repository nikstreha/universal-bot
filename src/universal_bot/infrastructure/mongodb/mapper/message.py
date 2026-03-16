from universal_bot.domain.value_object.message.message import Message
from universal_bot.infrastructure.mongodb.documents.message import MessageDocument


class MessageMapper:
    @staticmethod
    def to_document(message: Message) -> MessageDocument:
        return MessageDocument(
            id_=message.id_.value,
            role=message.role,
            content=message.content.value,
            created_at=message.created_at,
            reply_from=message.reply_from.value if message.reply_from else None,
            token_used=message.token_used.value if message.token_used else None,
        )
