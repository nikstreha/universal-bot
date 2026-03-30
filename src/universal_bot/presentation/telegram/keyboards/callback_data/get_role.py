from aiogram.filters.callback_data import CallbackData

from universal_bot.domain.enum.user.role import UserRole
from universal_bot.presentation.telegram.keyboards.callback_data.prefix import (
    CallbackMainPrefix,
)


class ChangeRoleCallback(CallbackData, prefix=CallbackMainPrefix.ADMIN):
    action: str
    prefix: str
    user_id: int
    role: UserRole
