from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from handlers.buttons import menu as btn


def main_menu_keyboard(admin: bool) -> InlineKeyboardBuilder:
    """Клавиатура главного меню"""
    keyboard = InlineKeyboardBuilder()

    keyboard.row(
        InlineKeyboardButton(text=f"{btn.PROFILE}", callback_data="menu|profile"),
        InlineKeyboardButton(text=f"{btn.BUY}", callback_data="menu|buy")
    )
    keyboard.row(
        # InlineKeyboardButton(text=f"{btn.BALANCE}", callback_data="menu|balance"),
        InlineKeyboardButton(text=f"{btn.KEYS}", callback_data="menu|keys")
    )

    if admin:
        keyboard.row(InlineKeyboardButton(text=f"{btn.ADMIN}", callback_data="menu|admin"))

    return keyboard
