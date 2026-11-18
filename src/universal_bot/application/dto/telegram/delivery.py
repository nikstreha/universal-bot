from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthorizedDeliveryDTO:
    id: str
    chat_id: int
    text: str
    lease_until: int
    created_at: int
    filename: str | None
    reply_to: int | None
    edit_message_id: int | None
