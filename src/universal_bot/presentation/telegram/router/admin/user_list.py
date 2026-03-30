from aiogram import F, Router, types
from aiogram.types import Message
from dishka.integrations.aiogram import FromDishka, inject

from universal_bot.application.dto.user.user_list import GetUserListRequestDTO
from universal_bot.application.query.admin.user_list import GetUserListInteractor
from universal_bot.presentation.telegram.keyboards.admin.buttons import AdminButtons
from universal_bot.presentation.telegram.keyboards.admin.inline_keypoard import (
    get_user_list_next_keyboard,
)

router = Router()

_PAGE_SIZE = 20


def _build_user_list_text(users: list) -> str:
    lines = [
        f"{i + 1}. {u.user_name or '—'} | <code>{u.id_}</code> | {u.role}"
        for i, u in enumerate(users)
    ]
    return "Users:\n\n" + "\n".join(lines)


@router.message(F.text == AdminButtons.USER_LIST)
@inject
async def handle_user_list(
    message: types.Message,
    get_user_list: FromDishka[GetUserListInteractor],
) -> None:
    if not message.from_user:
        return

    users = await get_user_list(
        GetUserListRequestDTO(user_id=message.from_user.id, limit=_PAGE_SIZE)
    )

    if not users:
        await message.answer("No users found.")
        return

    keyboard = get_user_list_next_keyboard() if len(users) == _PAGE_SIZE else None
    await message.answer(
        _build_user_list_text(users), parse_mode="HTML", reply_markup=keyboard
    )


@router.callback_query(F.data == "admin:user_list_next")
@inject
async def handle_user_list_next(
    callback: types.CallbackQuery,
    get_user_list: FromDishka[GetUserListInteractor],
) -> None:
    if not isinstance(callback.message, Message):
        await callback.answer("Message is no longer available.")
        return

    users = await get_user_list(
        GetUserListRequestDTO(user_id=callback.from_user.id, limit=_PAGE_SIZE)
    )

    if not users:
        await callback.message.edit_text("No more users.")
        await callback.answer()
        return

    keyboard = get_user_list_next_keyboard() if len(users) == _PAGE_SIZE else None
    await callback.message.edit_text(
        _build_user_list_text(users), parse_mode="HTML", reply_markup=keyboard
    )
    await callback.answer()
