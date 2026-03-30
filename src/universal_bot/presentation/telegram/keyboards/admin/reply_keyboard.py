from aiogram.types import ReplyKeyboardMarkup

from universal_bot.presentation.telegram.keyboards.admin.buttons import AdminButtons
from universal_bot.presentation.telegram.keyboards.reply_keyboard_factory import (
    ReplyKeyboardFactory,
)


def get_admin_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardFactory.build(AdminButtons, buttons_per_row=2)
