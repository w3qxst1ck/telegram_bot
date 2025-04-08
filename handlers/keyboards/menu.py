from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from handlers.buttons import menu as btn
from handlers.buttons import commands as cmd
from settings import settings


def main_menu_keyboard(admin: bool) -> InlineKeyboardBuilder:
    """Клавиатура главного меню"""
    keyboard = InlineKeyboardBuilder()

    keyboard.row(
        InlineKeyboardButton(text=f"{btn.KEYS}", callback_data="menu|keys"),
        InlineKeyboardButton(text=f"{btn.BUY}", callback_data="menu|buy"),
    )
    keyboard.row(
        InlineKeyboardButton(text=f"{btn.BALANCE}", callback_data="menu|balance"),
        InlineKeyboardButton(text=f"{btn.PAYMENTS}", callback_data="menu|payments")
    )

    keyboard.row(InlineKeyboardButton(text=f"Пользовательское соглашение", url=f"{settings.user_agreement_link}"))

    if admin:
        keyboard.row(InlineKeyboardButton(text=f"{btn.ADMIN}", callback_data="menu|admin"))

    return keyboard


def to_menu_keyboard() -> InlineKeyboardBuilder:
    """Клавиатура с кнопкой назад в получении пробного ключа"""
    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text=f"{cmd.MENU[1]}", callback_data="menu"))

    return keyboard