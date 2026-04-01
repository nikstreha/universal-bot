from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from universal_bot.presentation.telegram.callback_data.admin.prefix import (
    PrefixCallback,
)
from universal_bot.presentation.telegram.keyboards.admin.buttons import AdminButtons
from universal_bot.presentation.telegram.keyboards.admin.reply_keyboard import (
    get_admin_keyboard,
)
from universal_bot.presentation.telegram.keyboards.main.reply_keyboard import (
    get_main_keyboard,
)

router = Router()


@router.message(F.text == AdminButtons.EXIT)
async def handle_exit_admin(message: types.Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Exited admin panel.", reply_markup=get_main_keyboard())


@router.message(Command("cancel"))
async def handle_cancel_command(message: types.Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Cancelled.", reply_markup=get_admin_keyboard())


@router.callback_query(F.data == PrefixCallback.CANCEL)
async def handle_cancel_callback(
    callback: types.CallbackQuery,
    state: FSMContext,
) -> None:
    if not isinstance(callback.message, Message):
        await callback.answer("Message is no longer available.")
        return

    await state.clear()

    await callback.message.edit_text("Cancelled.")
    await callback.answer()
