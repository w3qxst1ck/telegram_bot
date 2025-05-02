from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from handlers.buttons import menu as btn


def admin_keyboard() -> InlineKeyboardBuilder:
    """Меню администратора"""
    keyboard = InlineKeyboardBuilder()

    keyboard.row(InlineKeyboardButton(text=f"{btn.NOTIFY}", callback_data="notify_users"))
    keyboard.row(InlineKeyboardButton(text=f"{btn.STATS}", callback_data="stats"))

    keyboard.row(InlineKeyboardButton(text=f"{btn.BACK}", callback_data="menu"))

    return keyboard


def admin_users_group() -> InlineKeyboardBuilder:
    """Группы пользователей для рассылки"""
    keyboard = InlineKeyboardBuilder()

    keyboard.row(InlineKeyboardButton(text="Всем пользователям", callback_data="users_group|all"))
    keyboard.row(InlineKeyboardButton(text="Польз. с активными ключами", callback_data="users_group|active"))
    keyboard.row(InlineKeyboardButton(text="Польз. без активных ключей", callback_data="users_group|expired"))

    keyboard.row(InlineKeyboardButton(text=f"{btn.BACK}", callback_data="menu|admin"))

    return keyboard


def back_button() -> InlineKeyboardBuilder:
    """Кнопка назад для рассылки при ожидании сообщения"""
    keyboard = InlineKeyboardBuilder()

    keyboard.row(InlineKeyboardButton(text=f"{btn.BACK}", callback_data="notify_users"))

    return keyboard


def back_to_admin_menu() -> InlineKeyboardBuilder:
    """Кнопка возращения в меню администратора"""
    keyboard = InlineKeyboardBuilder()

    keyboard.row(InlineKeyboardButton(text=f"{btn.BACK}", callback_data="menu|admin"))

    return keyboard
