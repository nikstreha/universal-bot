from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

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
    """Exit the admin panel.

    Clears FSM state and restores the main reply keyboard.
    """
    await state.clear()
    await message.answer("Exited admin panel.", reply_markup=get_main_keyboard())


@router.message(Command("cancel"))
async def handle_cancel_command(message: types.Message, state: FSMContext) -> None:
    """Handle /cancel command.

    Aborts the current admin operation, clears FSM state,
    and returns the admin keyboard.
    """
    await state.clear()
    await message.answer("Cancelled.", reply_markup=get_admin_keyboard())
