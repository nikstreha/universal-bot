import asyncio
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, CommandStart

from api.telegram.router.admin_handlers import router
from core.config import settings






async def main():
    dp = Dispatcher()

    dp.include_router(router)

    logging.basicConfig(level=logging.DEBUG)
    bot = Bot(token=settings.BOT_TOKEN)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
