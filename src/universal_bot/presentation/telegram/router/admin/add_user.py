from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from dishka.integrations.aiogram import FromDishka

from universal_bot.application.command.admin.add_user import AddUserInteractor
from universal_bot.application.dto.user.user import AddUserDTO
from universal_bot.domain.enum.user.role import UserRole
from universal_bot.presentation.telegram.keyboards.admin.buttons import AdminButtons
from universal_bot.presentation.telegram.keyboards.admin.inline_keypoard import (
    get_role_keyboard,
)
from universal_bot.presentation.telegram.states.admin_states import AdminStates

router = Router()


@router.message(F.text == AdminButtons.ADD_USER)
async def handle_add_user_start(message: types.Message, state: FSMContext) -> None:
    await state.set_state(AdminStates.add_user_enter_id)
    await message.answer("Enter user ID to add (or /cancel to abort):")


@router.message(AdminStates.add_user_enter_id)
async def handle_add_user_enter_id(
    message: types.Message,
    state: FSMContext,
) -> None:
    text = (message.text or "").strip()
    if not text.lstrip("-").isdigit():
        await message.answer("Invalid ID. Please enter a numeric user ID:")
        return

    user_id = int(text)
    await state.clear()
    await message.answer(
        f"Adding user <code>{user_id}</code>. Select role:",
        parse_mode="HTML",
        reply_markup=get_role_keyboard(user_id, "add_role"),
    )


@router.callback_query(F.data.startswith("admin:add_role:"))
async def handle_add_role_confirm(
    callback: types.CallbackQuery,
    add_user: FromDishka[AddUserInteractor],
) -> None:
    if not isinstance(callback.message, Message):
        await callback.answer("Message is no longer available.")
        return

    parts = callback.data.split(":")  # type: ignore[union-attr]
    user_id = int(parts[2])
    role = UserRole(parts[3])
    try:
        await add_user(AddUserDTO(user_id=user_id, role=role, user_name=None))
        await callback.message.edit_text(
            f"User <code>{user_id}</code> added with role <b>{role}</b>.",
            parse_mode="HTML",
        )
    except Exception as e:
        await callback.message.edit_text(f"Error: {e}")
    await callback.answer()
