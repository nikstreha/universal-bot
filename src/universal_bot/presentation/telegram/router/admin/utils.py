import html

from universal_bot.application.dto.user.user import UserDocumentDTO


def format_user(user: UserDocumentDTO) -> str:
    """Return an HTML-formatted string with the user's key fields."""
    name = html.escape(user.user_name) if user.user_name else "—"
    return (
        f"ID: <code>{user.id_}</code>\n"
        f"Name: {name}\n"
        f"Role: <b>{user.role}</b>\n"
        f"Last seen: {user.touched_at.strftime('%Y-%m-%d %H:%M UTC')}"
    )


def extract_id(text: str) -> int:
    if not text.lstrip("-").isdigit():
        raise ValueError("Invalid ID. Please enter a numeric ID.")

    id_ = int(text)
    if id_ <= 0:
        raise ValueError("ID must be greater than 0.")

    return id_
