from backend_component.domain.value_object.message.message import Message
from backend_component.infrastructure.mongodb.models.message import MessageDocument


class MessageMapper:
    @staticmethod
    def to_document(message: Message) -> MessageDocument:
        return MessageDocument(
            id_=message.id_.value,
            role=message.role.value,
            content=message.content.value,
            created_at=message.created_at,
            reply_from=message.reply_from.value if message.reply_from else None,
            token_used=message.token_used.value if message.token_used else None,
        )