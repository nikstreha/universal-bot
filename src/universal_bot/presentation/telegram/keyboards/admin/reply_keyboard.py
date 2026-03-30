from aiogram.types import (
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from universal_bot.presentation.telegram.keyboards.admin.buttons import AdminButtons


def get_admin_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=AdminButtons.BAN_USER),
                KeyboardButton(text=AdminButtons.CHANGE_ROLE),
            ],
            [
                KeyboardButton(text=AdminButtons.ADD_USER),
                KeyboardButton(text=AdminButtons.USER_LIST),
            ],
            [KeyboardButton(text=AdminButtons.LOOKUP_USER)],
            [KeyboardButton(text=AdminButtons.EXIT)],
        ],
        resize_keyboard=True,
    )
