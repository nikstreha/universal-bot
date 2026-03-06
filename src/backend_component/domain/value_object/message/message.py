from datetime import datetime
from backend_component.domain.enum.message.role import MessageRole
from backend_component.domain.value_object.message.content import MessageContent
from backend_component.domain.value_object.message.token_used import TokenUsed


from backend_component.domain.value_object.message.id import MessageId


from dataclasses import dataclass


@dataclass(frozen=True, slots=True, repr=False)
class Message:
    id_: MessageId
    role: MessageRole
    content: MessageContent
    created_at: datetime
    reply_from: MessageId | None = None
    token_used: TokenUsed | None = None
