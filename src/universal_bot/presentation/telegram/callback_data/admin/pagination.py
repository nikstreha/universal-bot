from aiogram.filters.callback_data import CallbackData

from universal_bot.presentation.telegram.callback_data.admin.prefix import (
    AdminCallbackPrefix,
    PrefixCallback,
)


class PaginationCallback(CallbackData, prefix=AdminCallbackPrefix.ADMIN):
    action: str
    prefix: str = PrefixCallback.PAGINATION
    cursor: int = 0


"""class UserListCallback(CallbackData, prefix=AdminCallbackPrefix.MESSAGE):
    action: str = AdminActions.NEXT_USER_LIST
    prefix: str = PrefixCallback.USER_LIST
    cursor: int = 0"""
