from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardRemove

# from api.managers.admin_manager import get_admins
from universal_bot.presentation.telegram.keyboards.admin_keyboard import (
    AdminButgtons,
    get_admin_keyboard,
)

bot_router = Router()
admins = 775965340  # temporary


@bot_router.message(F.text == AdminButgtons.ADD_USER)
async def add_user(message: types.Message) -> None:
    await message.answer(text="Add user", reply_markup=get_admin_keyboard())


@bot_router.message(F.text == AdminButgtons.REMOVE_USER)
async def remove_user(message: types.Message) -> None:
    await message.answer(text="Remove user", reply_markup=get_admin_keyboard())


@bot_router.message(F.text == AdminButgtons.STOP_ADMIN)
async def stop_admin(message: types.Message) -> None:
    await message.answer(text="Stop admin", reply_markup=ReplyKeyboardRemove())


@bot_router.message(Command("admin"))
async def handle_admin(message: types.Message) -> None:
    if message.from_user:
        user_id = message.from_user.id
        print(user_id)

    await message.answer(text="You are an admin", reply_markup=get_admin_keyboard())
