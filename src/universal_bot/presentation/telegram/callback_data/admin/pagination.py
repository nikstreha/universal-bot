from aiogram.filters.callback_data import CallbackData

from universal_bot.presentation.telegram.callback_data.admin.prefix import (
    AdminCallbackPrefix,
    PrefixCallback,
)


class PaginationCallback(CallbackData, prefix=AdminCallbackPrefix.ADMIN):
    action: str
    prefix: str = PrefixCallback.PAGINATION
    cursor: int = 0
