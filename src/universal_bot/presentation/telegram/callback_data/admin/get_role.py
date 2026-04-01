from aiogram.filters.callback_data import CallbackData

from universal_bot.domain.enum.user.role import UserRole
from universal_bot.presentation.telegram.callback_data.admin.prefix import (
    AdminCallbackPrefix,
)


class GetRoleCallback(CallbackData, prefix=AdminCallbackPrefix.CHANGE_ROLE):
    action: str
    prefix: str | None = None
    user_id: int
    role: UserRole
