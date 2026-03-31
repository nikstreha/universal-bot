from aiogram import Router

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
