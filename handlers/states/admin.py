from aiogram.fsm.state import StatesGroup, State


class NotifyUsersFSM(StatesGroup):
    text = State()