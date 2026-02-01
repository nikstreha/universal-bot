import asyncio
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, CommandStart

from core.config import settings

bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher()


@dp.message(Command("help"))
async def hendle_help(message: types.Message):
    await message.answer(text="I'm a helper")


@dp.message()
async def handle_start(message: types.Message):
    print(message.chat.id)
    print(message.photo[-1])
    await message.answer_photo(photo=message.photo[0].file_id)


async def main():
    logging.basicConfig(level=logging.DEBUG)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
