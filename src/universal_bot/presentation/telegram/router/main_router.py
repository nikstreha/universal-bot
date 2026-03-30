from aiogram import Router

from universal_bot.presentation.telegram.router.admin import admin_router
from universal_bot.presentation.telegram.router.system.system_handler import (
    router as system_router,
)

root_router = Router()

root_router.include_router(system_router)
root_router.include_router(admin_router)
