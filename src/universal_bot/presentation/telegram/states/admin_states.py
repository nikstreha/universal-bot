from aiogram.fsm.state import State, StatesGroup


class AdminStates(StatesGroup):
    ban_enter_id = State()
    update_role_enter_id = State()
    add_user_enter_id = State()
    lookup_enter_id = State()
