from aiogram import F, Router, types
from aiogram.types import Message
from dishka.integrations.aiogram import FromDishka, inject

from universal_bot.application.dto.messages.unknown import (
    GetAdminMessagesDTO,
    UnknownMessageDTO,
)
from universal_bot.application.query.admin.get_admin_messages import (
    GetAdminMessagesInteractor,
)
from universal_bot.presentation.telegram.callback_data.admin.actions import AdminActions
from universal_bot.presentation.telegram.callback_data.admin.pagination import (
    PaginationCallback,
)
from universal_bot.presentation.telegram.keyboards.admin.buttons import (
    ActionButtons,
    AdminButtons,
)
from universal_bot.presentation.telegram.keyboards.admin.inline_keyboard import (
    get_admin_messages_next_keyboard,
)

router = Router()


def _build_admin_messages_text(msg_collection: list[UnknownMessageDTO]) -> str:
    lines = [
        f"{msg.message or '—'} | <code>{msg.user_id}</code> | {msg.created_at.isoformat()}"
        for msg in msg_collection
    ]
    return "Messages:\n\n" + "\n".join(lines)


@router.message(F.text == AdminButtons.MESSAGE_FOR_ADMIN)
@inject
async def handle_messages_for_admin(
    message: types.Message,
    interactor: FromDishka[GetAdminMessagesInteractor],
) -> None:
    if not message.from_user:
        return

    message_collection = await interactor(GetAdminMessagesDTO())

    if not message_collection:
        await message.answer("No messages found.")
        return

    keyboard = (
        get_admin_messages_next_keyboard(message_collection.next_cursor)
        if message_collection.next_cursor
        else None
    )
    await message.answer(
        _build_admin_messages_text(message_collection.messages),
        parse_mode="HTML",
        reply_markup=keyboard,
    )


@router.callback_query(PaginationCallback.filter(F.action == AdminActions.NEXT_MESSAGES))
@inject
async def handle_admin_messages_next(
    callback: types.CallbackQuery,
    callback_data: PaginationCallback,
    interactor: FromDishka[GetAdminMessagesInteractor],
) -> None:
    if not isinstance(callback.message, Message):
        await callback.answer("Message is no longer available.")
        return

    message_collection = await interactor(
        GetAdminMessagesDTO(cursor=callback_data.cursor)
    )

    if not message_collection:
        await callback.message.edit_text("No more messages.")
        await callback.answer()
        return

    keyboard = (
        get_admin_messages_next_keyboard(message_collection.next_cursor)
        if message_collection.next_cursor
        else None
    )
    await callback.message.edit_text(
        _build_admin_messages_text(message_collection.messages),
        parse_mode="HTML",
        reply_markup=keyboard,
    )
    await callback.answer()
