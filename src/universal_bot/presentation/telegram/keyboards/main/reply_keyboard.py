from aiogram.types import ReplyKeyboardMarkup

from universal_bot.presentation.telegram.keyboards.main.buttons import MainButtons
from universal_bot.presentation.telegram.keyboards.reply_keyboard_factory import (
    ReplyKeyboardFactory,
)


def get_main_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardFactory.build(MainButtons)
