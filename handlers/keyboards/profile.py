from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def profile_keyboard(active: bool) -> InlineKeyboardBuilder:
    """Клавиатура профиля пользователя"""
    keyboard = InlineKeyboardBuilder()

    if not active:
        # TODO поменять на кнопку из файла
        keyboard.row(InlineKeyboardButton(text="Пополнить баланс", callback_data="balance"))
    keyboard.row(InlineKeyboardButton(text="🔙 назад", callback_data="back-to-menu"))
    keyboard.adjust(1)

    return keyboard

