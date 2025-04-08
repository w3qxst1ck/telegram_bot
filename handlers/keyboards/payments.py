from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from handlers.buttons import menu as btn


def back_to_main_menu() -> InlineKeyboardBuilder:
    """Кнопка возврата в главное меню"""
    keyboard = InlineKeyboardBuilder()

    keyboard.row(InlineKeyboardButton(text=f"{btn.BACK}", callback_data="menu"))

    return keyboard