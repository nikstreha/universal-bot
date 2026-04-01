import html

from aiogram import F, Router, types
from aiogram.types import Message
from dishka.integrations.aiogram import FromDishka, inject

from universal_bot.application.dto.user.user_list import GetUserListRequestDTO
from universal_bot.application.query.admin.user_list import GetUserListInteractor
from universal_bot.presentation.telegram.callback_data.admin.actions import AdminActions
from universal_bot.presentation.telegram.callback_data.admin.pagination import (
    PaginationCallback,
)
from universal_bot.presentation.telegram.keyboards.admin.buttons import (
    ActionButtons,
    AdminButtons,
)
from universal_bot.presentation.telegram.keyboards.admin.inline_keyboard import (
    get_user_list_next_keyboard,
)

router = Router()

_PAGE_SIZE = 20


def _build_user_list_text(users: list) -> str:
    lines = [
        f"{i + 1}. {html.escape(u.user_name) if u.user_name else '—'} | <code>{u.id_}</code> | {u.role}"
        for i, u in enumerate(users)
    ]
    return "Users:\n\n" + "\n".join(lines)


@router.message(F.text == AdminButtons.USER_LIST)
@inject
async def handle_user_list(
    message: types.Message,
    interactor: FromDishka[GetUserListInteractor],
) -> None:
    if not message.from_user:
        return

    response = await interactor(
        GetUserListRequestDTO(user_id=message.from_user.id, limit=_PAGE_SIZE)
    )

    if not response.user_list:
        await message.answer("No users found.")
        return

    keyboard = (
        get_user_list_next_keyboard(response.cursor if response.cursor else 0)
        if len(response.user_list) == _PAGE_SIZE
        else None
    )
    await message.answer(
        _build_user_list_text(response.user_list),
        parse_mode="HTML",
        reply_markup=keyboard,
    )


@router.callback_query(PaginationCallback.filter(F.action == AdminActions.NEXT_USER_LIST))
@inject
async def handle_user_list_next(
    callback: types.CallbackQuery,
    callback_data: PaginationCallback,
    interactor: FromDishka[GetUserListInteractor],
) -> None:
    cursor = callback_data.cursor

    if not isinstance(callback.message, Message):
        await callback.answer("Message is no longer available.")
        return

    response = await interactor(
        GetUserListRequestDTO(
            user_id=callback.from_user.id, limit=_PAGE_SIZE, after_id=cursor
        )
    )

    if not response.user_list:
        await callback.message.edit_text("No more users.")
        await callback.answer()
        return

    keyboard = (
        get_user_list_next_keyboard(response.cursor if response.cursor else 0)
        if len(response.user_list) == _PAGE_SIZE
        else None
    )
    await callback.message.edit_text(
        _build_user_list_text(response.user_list),
        parse_mode="HTML",
        reply_markup=keyboard,
    )
    await callback.answer()
