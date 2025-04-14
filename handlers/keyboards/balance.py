from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from handlers.buttons import menu as btn
from settings import settings


def payment_confirm_keyboard(summ: str) -> InlineKeyboardBuilder:
    """Клавиатура с кнопкой подтверждения оплаты"""
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(
            text="Оплатил(а)", callback_data=f"paid|{summ}")
    )
    keyboard.row(InlineKeyboardButton(text=f"{btn.BACK}", callback_data="menu|balance"))

    return keyboard


def choose_payment_method_keyboard(need_back_button: bool = True) -> InlineKeyboardBuilder:
    """Выбор способа оплаты"""
    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text="Перевод на карту 💳", callback_data=f"pay_method_transfer"))
    keyboard.row(InlineKeyboardButton(text="Звездами телеграм ⭐️", callback_data=f"pay_method_star"))

    if settings.need_payment_service:
        keyboard.row(InlineKeyboardButton(text="Картой", callback_data=f"pay_method_card"))

    if need_back_button:
        keyboard.row(InlineKeyboardButton(text=f"{btn.BACK}", callback_data="menu"))
    return keyboard


def payment_confirm_admin_keyboard(tg_id: str, summ: str, payment_id: int) -> InlineKeyboardBuilder:
    """Клавиатура для подтверждения или отклонения платежа админом"""
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(text="Подтвердить ✅", callback_data=f"admin-payment-confirm|{tg_id}|{summ}|{payment_id}"),
        InlineKeyboardButton(text="Отклонить ❌", callback_data=f"admin-payment-cancel|{tg_id}|{summ}|{payment_id}")
    )
    return keyboard


def not_enough_balance_new_key_keyboard(country: str) -> InlineKeyboardBuilder:
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


def back_to_choose_payment_method() -> InlineKeyboardBuilder:
    """Возвращение в меню из перевода на карту в выбор способа оплаты"""
    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text=f"{btn.BACK}", callback_data="menu|balance"))
    return keyboard
