from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class TelegramMessageDTO:
    message_id: int
