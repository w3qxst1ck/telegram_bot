from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from handlers.buttons import menu as btn


def keys_keyboard(back_btn: bool = False) -> InlineKeyboardBuilder:
    """Клавиатура профиля пользователя"""
    keyboard = InlineKeyboardBuilder()

    if back_btn:
        keyboard.row(InlineKeyboardButton(text=f"{btn.BACK}", callback_data="menu"))
    keyboard.adjust(1)

    return keyboard

