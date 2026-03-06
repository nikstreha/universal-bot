from aiogram import types, Router
from aiogram.filters import Command, CommandStart


router = Router()


@router.message(CommandStart)
async def handle_start(message: types.Message) -> None:
    user_id = message.from_user.id
    user_name = message.from_user.username

    await message.answer_photo(photo=message.photo[0].file_id)


@router.message(Command("help"))
async def hendle_help(message: types.Message) -> None:
    
    await message.answer(text="I'm a helper")
