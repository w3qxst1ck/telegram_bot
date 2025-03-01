from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from handlers.buttons import menu as btn


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


def cancel_keyboard() -> InlineKeyboardBuilder:
    """Клавиатура для отмены пополнения баланса"""
    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text="❌ Отмена", callback_data="button_cancel"))
    return keyboard