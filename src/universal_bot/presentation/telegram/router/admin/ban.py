from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from dishka.integrations.aiogram import FromDishka

from universal_bot.application.command.admin.ban import BanUserInteractor
from universal_bot.application.query.admin.get_user import GetUserInteractor
from universal_bot.presentation.telegram.keyboards.admin.buttons import AdminButtons
from universal_bot.presentation.telegram.keyboards.admin.inline_keypoard import (
    get_ban_confirm_keyboard,
)
from universal_bot.presentation.telegram.router.admin.utils import format_user
from universal_bot.presentation.telegram.states.admin_states import AdminStates

router = Router()


@router.message(F.text == AdminButtons.BAN_USER)
async def handle_ban_start(message: types.Message, state: FSMContext) -> None:
    await state.set_state(AdminStates.ban_enter_id)
    await message.answer("Enter user ID to ban (or /cancel to abort):")


@router.message(AdminStates.ban_enter_id)
async def handle_ban_enter_id(
    message: types.Message,
    state: FSMContext,
    get_user: FromDishka[GetUserInteractor],
) -> None:
    text = (message.text or "").strip()
    if not text.lstrip("-").isdigit():
        await message.answer("Invalid ID. Please enter a numeric user ID:")
        return

    user_id = int(text)
    user = await get_user(user_id)

    if not user:
        await message.answer("User not found. Enter another ID or /cancel:")
        return

    await state.clear()
    await message.answer(
        f"User found:\n\n{format_user(user)}\n\nConfirm action:",
        parse_mode="HTML",
        reply_markup=get_ban_confirm_keyboard(user_id),
    )


@router.callback_query(F.data.startswith("admin:ban:"))
async def handle_ban_confirm(
    callback: types.CallbackQuery,
    ban_user: FromDishka[BanUserInteractor],
) -> None:
    if not isinstance(callback.message, Message):
        await callback.answer("Message is no longer available.")
        return

    user_id = int(callback.data.split(":")[2])  # type: ignore[union-attr]
    try:
        await ban_user(user_id)
        await callback.message.edit_text(
            f"User <code>{user_id}</code> has been banned.", parse_mode="HTML"
        )

    except ValueError as e:
        await callback.message.edit_text(str(e))
    await callback.answer()
