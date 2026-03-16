import asyncio
import logging

from aiogram import Bot, Dispatcher

from universal_bot.composition.configuration.config import settings
from universal_bot.presentation.telegram.router.admin_handlers import router


async def register_bot() -> None:
    dp = Dispatcher()
    dp.include_router(router)

    logging.basicConfig(level=logging.DEBUG)
    bot = Bot(token=settings.BOT_TOKEN)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(register_bot())
