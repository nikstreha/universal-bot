from aiogram.filters.callback_data import CallbackData

from universal_bot.presentation.telegram.keyboards.admin.buttons import AdminButtons
from universal_bot.presentation.telegram.keyboards.callback_data.prefix import (
    CallbackMainPrefix,
    PrefixCallback,
)


class BanUserCallback(CallbackData, prefix=CallbackMainPrefix.ADMIN):
    action: str = AdminButtons.BAN_USER
    prefix: str = PrefixCallback.BAN_PROMPT
    user_id: int


class ChangeUserRoleCallback(CallbackData, prefix=CallbackMainPrefix.ADMIN):
    action: str = AdminButtons.CHANGE_ROLE
    prefix: str = PrefixCallback.ROLE_PROMPT
    user_id: int
