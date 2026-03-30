from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from dishka.integrations.aiogram import FromDishka, inject

from universal_bot.application.query.admin.get_user import GetUserInteractor
from universal_bot.presentation.telegram.keyboards.admin.buttons import AdminButtons
from universal_bot.presentation.telegram.keyboards.admin.inline_keypoard import (
    get_ban_confirm_keyboard,
    get_role_keyboard,
    get_user_actions_keyboard,
)
from universal_bot.presentation.telegram.router.admin.utils import format_user
from universal_bot.presentation.telegram.states.admin_states import AdminStates

router = Router()


@router.message(F.text == AdminButtons.LOOKUP_USER)
async def handle_lookup_start(message: types.Message, state: FSMContext) -> None:
    await state.set_state(AdminStates.lookup_enter_id)
    await message.answer("Enter user ID (or /cancel to abort):")


@router.message(AdminStates.lookup_enter_id)
@inject
async def handle_lookup_enter_id(
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
        format_user(user),
        parse_mode="HTML",
        reply_markup=get_user_actions_keyboard(user_id),
    )


@router.callback_query(F.data.startswith("admin:ban_prompt:"))
async def handle_ban_prompt(callback: types.CallbackQuery) -> None:
    if not isinstance(callback.message, Message):
        await callback.answer("Message is no longer available.")
        return

    user_id = int(callback.data.split(":")[2])  # type: ignore[union-attr]
    await callback.message.edit_reply_markup(
        reply_markup=get_ban_confirm_keyboard(user_id)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin:role_prompt:"))
async def handle_role_prompt(callback: types.CallbackQuery) -> None:
    if not isinstance(callback.message, Message):
        await callback.answer("Message is no longer available.")
        return

    user_id = int(callback.data.split(":")[2])  # type: ignore[union-attr]
    await callback.message.edit_reply_markup(
        reply_markup=get_role_keyboard(user_id, "set_role")
    )
    await callback.answer()
