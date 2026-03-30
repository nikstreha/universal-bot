"""Admin router package.

Assembles all admin sub-routers into a single ``admin_router``.
Attach admin-permission middleware here once it is ready:

    admin_router.message.middleware(AdminPermissionMiddleware())
    admin_router.callback_query.middleware(AdminPermissionMiddleware())
"""

from aiogram import F, Router, types
from aiogram.types import Message

from universal_bot.presentation.telegram.router.admin import (
    add_user,
    ban,
    common,
    lookup_user,
    update_role,
    user_list,
)

admin_router = Router()

# Navigation handlers first so /cancel and EXIT are never blocked by state filters
admin_router.include_router(common.router)
admin_router.include_router(ban.router)
admin_router.include_router(update_role.router)
admin_router.include_router(add_user.router)
admin_router.include_router(user_list.router)
admin_router.include_router(lookup_user.router)


# Shared inline cancel — lives on the parent router so it is reachable
# from any admin sub-flow regardless of which sub-router owns the message.
@admin_router.callback_query(F.data == "admin:cancel")
async def handle_cancel_callback(callback: types.CallbackQuery) -> None:
    """Handle the inline 'Cancel' button present on all admin confirmation keyboards.

    Replaces the inline message with a neutral 'Cancelled' notice.
    """
    if not isinstance(callback.message, Message):
        await callback.answer("Message is no longer available.")
        return

    await callback.message.edit_text("Cancelled.")
    await callback.answer()
