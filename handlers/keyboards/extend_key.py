from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from handlers.buttons import menu as btn
from handlers.buttons.regions import FLAGS
from schemas.user import UserConnList
from settings import settings


def extend_key_menu_keyboard(user_with_conns: UserConnList) -> InlineKeyboardBuilder:
    """Клавиатура для сообщения в меню продления ключей"""
    keyboard = InlineKeyboardBuilder()

    if user_with_conns.connections:
        for conn in user_with_conns.connections:
            emoji = "✅ " if conn.active else "❌ "
            flag = FLAGS[conn.region]
            keyboard.row(InlineKeyboardButton(
                text=f"{emoji}{flag} {conn.description}",
                callback_data=f"extend_key_email|{conn.email}")
            )

    keyboard.row(InlineKeyboardButton(text=f"{btn.BACK}", callback_data="menu|buy"))

    return keyboard


def extend_key_period_keyboard(email: str) -> InlineKeyboardBuilder:
    """Клавиатура для выбора периода продления ключа"""
    keyboard = InlineKeyboardBuilder()

    keyboard.row(
        InlineKeyboardButton(text=f"1 мес. ({settings.price_list['1']}р.)", callback_data=f"extend_key_period|1|{email}"),
        InlineKeyboardButton(text=f"3 мес. ({settings.price_list['3']}р.)", callback_data=f"extend_key_period|3|{email}")
    )
    keyboard.row(
        InlineKeyboardButton(text=f"6 мес. ({settings.price_list['6']}р.)", callback_data=f"extend_key_period|6|{email}"),
        InlineKeyboardButton(text=f"12 мес. ({settings.price_list['12']}р.)", callback_data=f"extend_key_period|12|{email}")
    )

    keyboard.row(InlineKeyboardButton(text=f"{btn.BACK}", callback_data="extend_key"))

    return keyboard


def extend_key_confirm_keyboard(period: str, email: str) -> InlineKeyboardBuilder:
    """Клавиатура для подтверждения продления ключа"""
    keyboard = InlineKeyboardBuilder()

    keyboard.row(
        InlineKeyboardButton(text=f"Да", callback_data=f"extend_key_confirm|{period}|{email}"),
        InlineKeyboardButton(text=f"Нет", callback_data=f"extend_key_email|{email}")
    )

    return keyboard