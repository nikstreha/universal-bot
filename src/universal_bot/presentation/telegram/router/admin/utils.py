from universal_bot.application.dto.user.user import UserDocumentDTO


def format_user(user: UserDocumentDTO) -> str:
    """Return an HTML-formatted string with the user's key fields."""
    name = user.user_name or "—"
    return (
        f"ID: <code>{user.id_}</code>\n"
        f"Name: {name}\n"
        f"Role: <b>{user.role}</b>\n"
        f"Last seen: {user.touched_at.strftime('%Y-%m-%d %H:%M UTC')}"
    )
