from aiogram.fsm.state import StatesGroup, State


class KeyDescriptionFSM(StatesGroup):
    description = State()