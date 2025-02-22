from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from handlers.buttons import menu as btn


def buy_keyboard(back_bnt: bool = None) -> InlineKeyboardBuilder:
    """Клавиатура сообщения с покупкой"""
    keyboard = InlineKeyboardBuilder()

    keyboard.row(InlineKeyboardButton(text=f"{btn.BUY}", callback_data="buy_sub"))
    keyboard.row(InlineKeyboardButton(text=f"{btn.BALANCE}", callback_data="balance"))

    if back_bnt:
        keyboard.row(InlineKeyboardButton(text=f"{btn.BACK}", callback_data="menu"))
    keyboard.adjust(1)

    return keyboard


def payment_confirm_keyboard() -> InlineKeyboardBuilder:
    """Клавиатура с кнопкой подтверждения оплаты"""
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(
            text="Оплатил(а)", callback_data=f"paid")
    )

    return keyboard


def cancel_keyboard() -> InlineKeyboardBuilder:
    """Клавиатура для отмены пополнения баланса"""
    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text="❌ Отмена", callback_data="button_cancel"))
    return keyboard