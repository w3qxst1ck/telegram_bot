from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def profile_keyboard(active: bool) -> InlineKeyboardBuilder:
    """Клавиатура профиля пользователя"""
    keyboard = InlineKeyboardBuilder()

    if not active:
        keyboard.row(InlineKeyboardButton(text="🔗 Подключить или продлить VPN", callback_data="connect-vpn"))
    keyboard.row(InlineKeyboardButton(text="🔙 назад", callback_data="back-to-start"))
    keyboard.adjust(1)

    return keyboard

