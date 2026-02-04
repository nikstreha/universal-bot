from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


class AdminButgtons:
    ADD_USER = "Add user"
    REMOVE_USER = "Remove user"
    STOP_ADMIN = "Stop admin"


def get_admin_keyboard() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=AdminButgtons.ADD_USER),
                KeyboardButton(text=AdminButgtons.REMOVE_USER),
            ],
            [
                KeyboardButton(text=AdminButgtons.STOP_ADMIN),
            ],
        ],
        resize_keyboard=True,
    )

    return keyboard
