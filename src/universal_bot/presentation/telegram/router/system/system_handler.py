from aiogram import F, Router, types
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext

from universal_bot.presentation.telegram.keyboards.admin.reply_keyboard import (
    get_admin_keyboard,
)
from universal_bot.presentation.telegram.keyboards.main.buttons import MainButtons
from universal_bot.presentation.telegram.keyboards.main.reply_keyboard import (
    get_main_keyboard,
)

router = Router()


@router.message(CommandStart())
async def handle_start(message: types.Message) -> None:
    if message.photo:
        await message.answer_photo(photo=message.photo[0].file_id)
    await message.answer("Welcome!", reply_markup=get_main_keyboard())


@router.message(Command("help"))
async def hendle_help(message: types.Message) -> None:
    await message.answer(text="I'm a helper")


@router.message(F.text == MainButtons.STUB)
async def handle_stub(message: types.Message) -> None:
    await message.answer("This feature is coming soon.")


@router.message(F.text == MainButtons.ADMIN)
async def handle_enter_admin(message: types.Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Admin panel", reply_markup=get_admin_keyboard())
