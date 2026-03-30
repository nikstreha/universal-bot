from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from universal_bot.presentation.telegram.keyboards.main.buttons import MainButtons


def get_main_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=MainButtons.ADMIN),
                KeyboardButton(text=MainButtons.STUB),
            ],
        ],
        resize_keyboard=True,
    )
