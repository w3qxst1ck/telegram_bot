from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from schemas.connection import ConnectionRegion
from handlers.buttons import menu as btn, regions


def keys_list(connections: list[ConnectionRegion]) -> InlineKeyboardBuilder:
    """Клавиатура со всеми ключами пользователя"""
    keyboard = InlineKeyboardBuilder()

    for conn in connections:
        flag = regions.FLAGS[conn.region]
        keyboard.row(InlineKeyboardButton(text=f"{flag} {conn.description}", callback_data=f"extra-traffic|{conn.id}"))

    keyboard.row(InlineKeyboardButton(text=f"{btn.BACK}", callback_data="menu|keys"))
    keyboard.adjust(1)

    return keyboard


def confirm_keyboard(conn_id: int) -> InlineKeyboardBuilder:
    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text=f"Подтвердить", callback_data=f"confirm_buy|{conn_id}"))
    keyboard.row(InlineKeyboardButton(text=f"{btn.BACK}", callback_data="buy-extra-traffic"))

    return keyboard

