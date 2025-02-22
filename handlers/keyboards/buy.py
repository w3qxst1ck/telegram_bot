from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from handlers.buttons import menu as btn


def buy_keyboard(back_bnt: bool = None) -> InlineKeyboardBuilder:
    """Клавиатура сообщения с покупкой"""
    keyboard = InlineKeyboardBuilder()

    keyboard.row(InlineKeyboardButton(text=f"{btn.BUY}", callback_data="buy_sub"))
    keyboard.row(InlineKeyboardButton(text=f"{btn.BALANCE}", callback_data="balance"))

    if back_bnt:
        keyboard.row(InlineKeyboardButton(text=f"{btn.BACK}", callback_data="menu"))
    keyboard.adjust(1)

    return keyboard