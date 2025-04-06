from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from handlers.buttons import menu as btn


def keys_keyboard(back_btn: bool = False) -> InlineKeyboardBuilder:
    """Клавиатура вкладки мои ключи"""
    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text=f"{btn.EXTRA_TRAFFIC}", callback_data="buy-extra-traffic"))
    keyboard.row(InlineKeyboardButton(text=f"{btn.DELETE_KEY}", callback_data="delete_key"))

    if back_btn:
        keyboard.row(InlineKeyboardButton(text=f"{btn.BACK}", callback_data="menu"))
    keyboard.adjust(1)

    return keyboard

