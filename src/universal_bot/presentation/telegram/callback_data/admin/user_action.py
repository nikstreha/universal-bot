from aiogram.filters.callback_data import CallbackData

from universal_bot.presentation.telegram.callback_data.admin.prefix import (
    AdminCallbackPrefix,
)


class BanUserCallback(CallbackData, prefix=AdminCallbackPrefix.BAN_USER):
    action: str
    prefix: str | None = None
    user_id: int


class ChangeUserRoleCallback(CallbackData, prefix=AdminCallbackPrefix.CHANGE_ROLE):
    action: str
    prefix: str | None = None
    user_id: int
