from aiogram import F, Router, types
from aiogram.types import Message

from universal_bot.presentation.telegram.router.admin import (
    add_user,
    admin_messages,
    ban,
    common,
    lookup_user,
    update_role,
    user_list,
)

admin_router = Router()

admin_router.include_router(common.router)
admin_router.include_router(ban.router)
admin_router.include_router(update_role.router)
admin_router.include_router(add_user.router)
admin_router.include_router(user_list.router)
admin_router.include_router(lookup_user.router)
admin_router.include_router(admin_messages.router)


@admin_router.callback_query(F.data == "admin:cancel")
async def handle_cancel_callback(callback: types.CallbackQuery) -> None:
    if not isinstance(callback.message, Message):
        await callback.answer("Message is no longer available.")
        return

    await callback.message.edit_text("Cancelled.")
    await callback.answer()
