from aiogram import Router, F, types

# from src.api.managers.admin_manager import get_admins

router = Router()
admins = (123456789) #temporary


@router.message(F.from_user.id.in_(admins))
async def handle_admin(message: types.Message):
    await message.answer(text="You are an admin")
