from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from handlers.buttons import menu as btn


def payment_confirm_keyboard(summ: str) -> InlineKeyboardBuilder:
    """Клавиатура с кнопкой подтверждения оплаты"""
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(
            text="Оплатил(а)", callback_data=f"paid|{summ}")
    )

    return keyboard


def payment_confirm_admin_keyboard(tg_id: str, summ: str) -> InlineKeyboardBuilder:
    """Клавиатура для подтверждения или отклонения платежа админом"""
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(text="Подтвердить ✅", callback_data=f"admin-payment-confirm|{tg_id}|{summ}"),
        InlineKeyboardButton(text="Отклонить ❌", callback_data=f"admin-payment-cancel|{tg_id}|{summ}")
    )
    return keyboard


def not_enough_balance_ney_key_keyboard(country: str) -> InlineKeyboardBuilder:
    """Клавиатура для сообщения при недостаточном балансе при покупке"""
    keyboard = InlineKeyboardBuilder()

    keyboard.row(InlineKeyboardButton(text=f"{btn.BALANCE}", callback_data="menu|balance"))
    keyboard.row(InlineKeyboardButton(text=f"{btn.BACK}", callback_data=f"new_key_country|{country}"))

    return keyboard


def not_enough_balance_extend_key_keyboard(eamil: str) -> InlineKeyboardBuilder:
    """Клавиатура для сообщения при недостаточном балансе при продлении"""
    keyboard = InlineKeyboardBuilder()

    keyboard.row(InlineKeyboardButton(text=f"{btn.BALANCE}", callback_data="menu|balance"))
    keyboard.row(InlineKeyboardButton(text=f"{btn.BACK}", callback_data=f"extend_key_email|{eamil}"))

    return keyboard


def cancel_keyboard() -> InlineKeyboardBuilder:
    """Клавиатура для отмены пополнения баланса"""
    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text="❌ Отмена", callback_data="button_cancel"))
    return keyboard


def back_to_menu_from_balance() -> InlineKeyboardBuilder:
    """Возвращение в меню из баланса и сброс FSM"""
    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text="❌ Отмена", callback_data="menu"))
    return keyboard
