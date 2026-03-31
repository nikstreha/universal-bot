from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from dishka.integrations.aiogram import FromDishka, inject

from universal_bot.application.command.admin.add_user import AddUserInteractor
from universal_bot.application.dto.user.user import AddUserDTO
from universal_bot.presentation.telegram.callback_data.admin.actions import AdminActions
from universal_bot.presentation.telegram.callback_data.admin.get_role import (
    GetRoleCallback,
)
from universal_bot.presentation.telegram.callback_data.admin.prefix import (
    PrefixCallback,
)
from universal_bot.presentation.telegram.keyboards.admin.buttons import AdminButtons
from universal_bot.presentation.telegram.keyboards.admin.inline_keyboard import (
    get_role_keyboard,
)
from universal_bot.presentation.telegram.router.admin.utils import extract_id
from universal_bot.presentation.telegram.states.admin_states import AdminStates

router = Router()


@router.message(F.text == AdminButtons.ADD_USER)
async def handle_add_user_start(message: types.Message, state: FSMContext) -> None:
    await state.set_state(AdminStates.add_user_enter_id)
    await message.answer("Enter user ID to add (or /cancel to abort):")


@router.message(AdminStates.add_user_enter_id, ~Command("cancel"))
async def handle_add_user_enter_id(
    message: types.Message,
    state: FSMContext,
) -> None:
    text = (message.text or "").strip()
    user_id = extract_id(text)

    await state.clear()
    await message.answer(
        f"Adding user <code>{user_id}</code>. Select role:",
        parse_mode="HTML",
        reply_markup=get_role_keyboard(user_id, AdminActions.ADD_ROLE),
    )


@router.callback_query(GetRoleCallback.filter(F.action == AdminActions.ADD_ROLE))
@inject
async def handle_add_role_confirm(
    callback: types.CallbackQuery,
    callback_data: GetRoleCallback,
    interactor: FromDishka[AddUserInteractor],
) -> None:
    if not isinstance(callback.message, Message):
        await callback.answer("Message is no longer available.")
        return

    try:
        await interactor(
            AddUserDTO(
                user_id=callback_data.user_id, role=callback_data.role, user_name=None
            )
        )
        await callback.message.edit_text(
            f"User <code>{callback_data.user_id}</code> added with role <b>{callback_data.role}</b>.",
            parse_mode="HTML",
        )
    except Exception as e:
        await callback.message.edit_text(f"Error: {e}")
    await callback.answer()
