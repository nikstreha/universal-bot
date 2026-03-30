from aiogram.filters.callback_data import CallbackData

from universal_bot.presentation.telegram.keyboards.admin.buttons import ActionButtons
from universal_bot.presentation.telegram.keyboards.callback_data.prefix import (
    CallbackMainPrefix,
    PrefixCallback,
)


class AdminMessagesCallback(CallbackData, prefix=CallbackMainPrefix.ADMIN):
    action: str = ActionButtons.NEXT
    prefix: str = PrefixCallback.ADMIN_MESSAGES
    cursor: int = 0


class UserListCallback(CallbackData, prefix=CallbackMainPrefix.ADMIN):
    action: str = ActionButtons.NEXT
    prefix: str = PrefixCallback.USER_LIST
    cursor: int = 0
