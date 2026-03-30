from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from universal_bot.domain.enum.user.role import UserRole


def get_ban_confirm_keyboard(user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✓ Confirm ban", callback_data=f"admin:ban:{user_id}"
                ),
                InlineKeyboardButton(text="✗ Cancel", callback_data="admin:cancel"),
            ]
        ]
    )


def get_role_keyboard(user_id: int, prefix: str) -> InlineKeyboardMarkup:
    roles = (role for role in UserRole)

    rows: list[list[InlineKeyboardButton]] = []
    row: list[InlineKeyboardButton] = []

    for role in roles:
        row.append(
            InlineKeyboardButton(
                text=role,
                callback_data=f"admin:{prefix}:{user_id}:{role.value}",
            )
        )
        if len(row) == 3:
            rows.append(row)
            row = []
    if row:
        rows.append(row)

    rows.append([InlineKeyboardButton(text="✗ Cancel", callback_data="admin:cancel")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def get_user_actions_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """Inline keyboard shown under a looked-up user's info card."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Ban", callback_data=f"admin:ban_prompt:{user_id}"
                ),
                InlineKeyboardButton(
                    text="Change role", callback_data=f"admin:role_prompt:{user_id}"
                ),
            ],
            [InlineKeyboardButton(text="✗ Cancel", callback_data="admin:cancel")],
        ]
    )


def get_user_list_next_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Next page →", callback_data="admin:user_list_next"
                )
            ]
        ]
    )
