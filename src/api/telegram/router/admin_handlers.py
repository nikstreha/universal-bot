from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardRemove

# from src.api.managers.admin_manager import get_admins
from src.api.telegram.keyboards.admin_keyboard import (
    AdminButgtons,
    get_admin_keyboard,
)

router = Router()
admins = (775965340)  # temporary


@router.message(F.text == AdminButgtons.ADD_USER)
async def add_user(message: types.Message) -> None:
    await message.answer(text="Add user", reply_markup=get_admin_keyboard())


@router.message(F.text == AdminButgtons.REMOVE_USER)
async def remove_user(message: types.Message) -> None:
    await message.answer(text="Remove user", reply_markup=get_admin_keyboard())


@router.message(F.text == AdminButgtons.STOP_ADMIN)
async def stop_admin(message: types.Message) -> None:
    await message.answer(reply_markup=ReplyKeyboardRemove())


@router.message(Command("admin"))
async def handle_admin(message: types.Message) -> None:
    print(message.from_user.id)
    await message.answer(
        text="You are an admin",
        reply_markup=get_admin_keyboard()
        )
