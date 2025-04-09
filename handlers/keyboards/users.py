from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from handlers.buttons import menu as btn


def choose_os() -> InlineKeyboardBuilder:
    """Клавиатура выбора ОС телефона"""
    keyboard = InlineKeyboardBuilder()

    keyboard.row(
        InlineKeyboardButton(text=f"{btn.IOS}", callback_data="instruction|iOS"),
        InlineKeyboardButton(text=f"{btn.ANDROID}", callback_data="instruction|Android")
    )
    keyboard.row(
        InlineKeyboardButton(text=f"{btn.MACOS}", callback_data="instruction|macOS"),
        InlineKeyboardButton(text=f"{btn.WINDOWS}", callback_data="instruction|Windows")
    )

    return keyboard
