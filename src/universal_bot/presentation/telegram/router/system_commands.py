from aiogram import Router, types
from aiogram.filters import Command, CommandStart

router = Router()


@router.message(CommandStart)
async def handle_start(message: types.Message) -> None:
    if message.from_user:
        user_id = message.from_user.id
        user_name = message.from_user.username

    if message.photo:
        await message.answer_photo(photo=message.photo[0].file_id)


@router.message(Command("help"))
async def hendle_help(message: types.Message) -> None:
    await message.answer(text="I'm a helper")
