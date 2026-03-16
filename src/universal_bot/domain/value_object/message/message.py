from dataclasses import dataclass
from datetime import datetime

from universal_bot.domain.enum.message.role import MessageRole
from universal_bot.domain.value_object.message.content import MessageContent
from universal_bot.domain.value_object.message.id import MessageId
from universal_bot.domain.value_object.message.token_used import TokenUsed


@dataclass(frozen=True, slots=True, repr=False)
class Message:
    id_: MessageId
    role: MessageRole
    content: MessageContent
    created_at: datetime
    reply_from: MessageId | None = None
    token_used: TokenUsed | None = None
