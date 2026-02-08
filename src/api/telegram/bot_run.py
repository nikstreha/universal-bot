import asyncio
import logging

from aiogram import Bot, Dispatcher
from src.api.telegram.router.admin_handlers import router
from src.core.config import settings


async def register_bot() -> None:
    dp = Dispatcher()
    dp.include_router(router)

    logging.basicConfig(level=logging.DEBUG)
    bot = Bot(token=settings.BOT_TOKEN)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(register_bot())
