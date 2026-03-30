from enum import StrEnum

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


class ReplyKeyboardFactory:
    @staticmethod
    def build(
        buttons_enum: type[StrEnum], buttons_per_row: int = 2
    ) -> ReplyKeyboardMarkup:
        values = list(buttons_enum)
        keyboard = [
            [KeyboardButton(text=value) for value in values[i : i + buttons_per_row]]
            for i in range(0, len(values), buttons_per_row)
        ]
        return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
