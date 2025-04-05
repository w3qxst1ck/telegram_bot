from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from handlers.buttons import menu as btn
from handlers.buttons.regions import FLAGS
from schemas.user import UserConnList


def delete_key_menu_keyboard(user_with_conns: UserConnList) -> InlineKeyboardBuilder:
    """Клавиатура для сообщения в меню удаления ключей"""
    keyboard = InlineKeyboardBuilder()

    for conn in user_with_conns.connections:
        emoji = "✅ " if conn.active else "❌ "
        flag = FLAGS[conn.region]
        keyboard.row(InlineKeyboardButton(
            text=f"{emoji}{flag} {conn.description}",
            callback_data=f"delete_key_email|{conn.email}")
        )

    keyboard.row(InlineKeyboardButton(text=f"{btn.BACK}", callback_data="menu|keys"))

    return keyboard


def confirm_delete_keyboard(email: str) -> InlineKeyboardBuilder:
    """Клавиатура подтверждения удаления ключа"""
    keyboard = InlineKeyboardBuilder()

    keyboard.row(
        InlineKeyboardButton(text=f"Да", callback_data=f"delete_key_confirm|{email}"),
        InlineKeyboardButton(text=f"Нет", callback_data="delete_key")
    )

    return keyboard