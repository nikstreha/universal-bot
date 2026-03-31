from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from dishka.integrations.aiogram import FromDishka, inject

from universal_bot.application.command.admin.update_role import UpdateRoleInteractor
from universal_bot.application.dto.user.user import UpdateUserRoleDTO
from universal_bot.application.query.admin.get_user import GetUserInteractor
from universal_bot.presentation.telegram.callback_data.admin.actions import AdminActions
from universal_bot.presentation.telegram.callback_data.admin.get_role import (
    GetRoleCallback,
)
from universal_bot.presentation.telegram.keyboards.admin.buttons import AdminButtons
from universal_bot.presentation.telegram.keyboards.admin.inline_keyboard import (
    get_role_keyboard,
)
from universal_bot.presentation.telegram.router.admin.utils import format_user
from universal_bot.presentation.telegram.states.admin_states import AdminStates

router = Router()


@router.message(F.text == AdminButtons.CHANGE_ROLE)
async def handle_update_role_start(message: types.Message, state: FSMContext) -> None:
    await state.set_state(AdminStates.update_role_enter_id)
    await message.answer("Enter user ID to change role (or /cancel to abort):")


@router.message(AdminStates.update_role_enter_id)
@inject
async def handle_update_role_enter_id(
    message: types.Message,
    state: FSMContext,
    interactor: FromDishka[GetUserInteractor],
) -> None:
    text = (message.text or "").strip()
    if not text.lstrip("-").isdigit():
        await message.answer("Invalid ID. Please enter a numeric user ID:")
        return

    user_id = int(text)
    user = await interactor(user_id)

    if not user:
        await message.answer("User not found. Enter another ID or /cancel:")
        return

    await state.clear()
    await message.answer(
        f"User found:\n\n{format_user(user)}\n\nSelect new role:",
        parse_mode="HTML",
        reply_markup=get_role_keyboard(user_id, AdminActions.SET_ROLE),
    )


@router.callback_query(GetRoleCallback.filter(F.action == AdminActions.SET_ROLE))
@inject
async def handle_change_role_confirm(
    callback: types.CallbackQuery,
    callback_data: GetRoleCallback,
    interactor: FromDishka[UpdateRoleInteractor],
) -> None:
    if not isinstance(callback.message, Message):
        await callback.answer("Message is no longer available.")
        return

    user_id = callback_data.user_id
    role = callback_data.role
    try:
        await interactor(UpdateUserRoleDTO(user_id=user_id, role=role))
        await callback.message.edit_text(
            f"Role of user <code>{user_id}</code> changed to <b>{role}</b>.",
            parse_mode="HTML",
        )

    except ValueError as e:
        await callback.message.edit_text(str(e))
    await callback.answer()
