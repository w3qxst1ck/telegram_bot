from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from handlers.buttons import menu as btn
from schemas.user import UserConnList
from settings import settings


# NEW KEY
def buy_keyboard(back_bnt: bool = None) -> InlineKeyboardBuilder:
    """Клавиатура сообщения с покупкой"""
    keyboard = InlineKeyboardBuilder()

    keyboard.row(InlineKeyboardButton(text=f"{btn.NEW_KEY}", callback_data="new_key"))
    keyboard.row(InlineKeyboardButton(text=f"{btn.EXTEND_KEY}", callback_data="extend_key"))
    keyboard.row(InlineKeyboardButton(text=f"{btn.BALANCE}", callback_data="balance"))

    if back_bnt:
        keyboard.row(InlineKeyboardButton(text=f"{btn.BACK}", callback_data="menu"))

    return keyboard


def new_key_keyboard() -> InlineKeyboardBuilder:
    """Клавиатура для покупки нового ключа"""
    keyboard = InlineKeyboardBuilder()

    keyboard.row(
        InlineKeyboardButton(text=f"1 мес. {settings.price_list['1']}р.", callback_data="new_key_period|1"),
        InlineKeyboardButton(text=f"3 мес. {settings.price_list['3']}р.", callback_data="new_key_period|3")
    )
    keyboard.row(
        InlineKeyboardButton(text=f"6 мес. {settings.price_list['6']}р.", callback_data="new_key_period|6"),
        InlineKeyboardButton(text=f"12 мес. {settings.price_list['12']}р.", callback_data="new_key_period|12")
    )

    keyboard.row(InlineKeyboardButton(text=f"{btn.BACK}", callback_data="menu|buy"))

    return keyboard


def new_key_confirm_keyboard(period: str) -> InlineKeyboardBuilder:
    """Клавиатура для подтверждения покупки ключа"""
    keyboard = InlineKeyboardBuilder()

    keyboard.row(
        InlineKeyboardButton(text=f"Да", callback_data=f"new_key_confirm|yes|{period}"),
        InlineKeyboardButton(text=f"Нет", callback_data=f"new_key_confirm|no|{period}")
    )

    return keyboard


# BALANCE
def payment_confirm_keyboard() -> InlineKeyboardBuilder:
    """Клавиатура с кнопкой подтверждения оплаты"""
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(
            text="Оплатил(а)", callback_data=f"paid")
    )

    return keyboard


def not_enough_balance_keyboard() -> InlineKeyboardBuilder:
    """Клавиатура для сообщения при недостаточном балансе"""
    keyboard = InlineKeyboardBuilder()

    keyboard.row(InlineKeyboardButton(text=f"{btn.BALANCE}", callback_data="balance"))
    keyboard.row(InlineKeyboardButton(text=f"{btn.BACK}", callback_data="new_key"))

    return keyboard


# EXTEND KEY
def extend_key_menu_keyboard(user_with_conns: UserConnList) -> InlineKeyboardBuilder:
    """Клавиатура для сообщения в меню продления ключей"""
    keyboard = InlineKeyboardBuilder()

    if user_with_conns.connections:
        for conn in user_with_conns.connections:
            emoji = "✅ " if conn.active else "❌ "
            keyboard.row(InlineKeyboardButton(
                text=f"{emoji}{conn.description}",
                callback_data=f"extend_key_period|{conn.email}")
            )

    keyboard.row(InlineKeyboardButton(text=f"{btn.BACK}", callback_data="menu|buy"))

    return keyboard


def cancel_keyboard() -> InlineKeyboardBuilder:
    """Клавиатура для отмены пополнения баланса"""
    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text="❌ Отмена", callback_data="button_cancel"))
    return keyboard