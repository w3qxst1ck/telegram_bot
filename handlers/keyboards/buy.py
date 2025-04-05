from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from handlers.buttons import menu as btn


def buy_keyboard(back_bnt: bool = None) -> InlineKeyboardBuilder:
    """Клавиатура сообщения с покупкой"""
    keyboard = InlineKeyboardBuilder()

    keyboard.row(InlineKeyboardButton(text=f"{btn.NEW_KEY}", callback_data="new_key"))
    keyboard.row(InlineKeyboardButton(text=f"{btn.EXTEND_KEY}", callback_data="extend_key"))

    if back_bnt:
        keyboard.row(InlineKeyboardButton(text=f"{btn.BACK}", callback_data="menu"))

    return keyboard
