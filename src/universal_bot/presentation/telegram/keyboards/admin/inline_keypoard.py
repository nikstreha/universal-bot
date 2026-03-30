from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from universal_bot.domain.enum.user.role import UserRole
from universal_bot.presentation.telegram.keyboards.admin.buttons import (
    ActionButtons,
    AdminButtons,
)
from universal_bot.presentation.telegram.keyboards.callback_data.get_role import (
    ChangeRoleCallback,
)
from universal_bot.presentation.telegram.keyboards.callback_data.pagination import (
    AdminMessagesCallback,
    UserListCallback,
)
from universal_bot.presentation.telegram.keyboards.callback_data.prefix import (
    PrefixCallback,
)
from universal_bot.presentation.telegram.keyboards.callback_data.user_action import (
    BanUserCallback,
    ChangeUserRoleCallback,
)


def get_ban_confirm_keyboard(user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"{ActionButtons.CONFIRM} ban",
                    callback_data=BanUserCallback(user_id=user_id).pack(),
                ),
                InlineKeyboardButton(
                    text=ActionButtons.CANCEL, callback_data=PrefixCallback.CANCEL
                ),
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
                callback_data=ChangeRoleCallback(
                    action=prefix,
                    prefix=prefix,
                    user_id=user_id,
                    role=role,
                ).pack(),
            ),
        )
        if len(row) == 3:
            rows.append(row)
            row = []
    if row:
        rows.append(row)

    rows.append(
        [
            InlineKeyboardButton(
                text=ActionButtons.CANCEL, callback_data=PrefixCallback.CANCEL
            )
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=rows)


def get_user_actions_keyboard(user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=AdminButtons.BAN_USER,
                    callback_data=BanUserCallback(user_id=user_id).pack(),
                ),
                InlineKeyboardButton(
                    text=AdminButtons.CHANGE_ROLE,
                    callback_data=ChangeUserRoleCallback(user_id=user_id).pack(),
                ),
            ],
            [
                InlineKeyboardButton(
                    text=ActionButtons.CANCEL, callback_data=PrefixCallback.CANCEL
                )
            ],
        ]
    )


def get_user_list_next_keyboard(cursor: int = 0) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=ActionButtons.NEXT,
                    callback_data=UserListCallback(cursor=cursor).pack(),
                )
            ]
        ]
    )


def get_admin_messages_next_keyboard(cursor: int = 0) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=ActionButtons.NEXT,
                    callback_data=AdminMessagesCallback(cursor=cursor).pack(),
                )
            ]
        ]
    )
