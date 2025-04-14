from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from handlers.buttons import menu as btn
from settings import settings


def choose_star_count_keyboard() -> InlineKeyboardBuilder:
    """Выбор количества звезд для пополнения"""
    keyboard = InlineKeyboardBuilder()

    for k, v in settings.stars_price_list.items():
        keyboard.row(InlineKeyboardButton(text=f"{k} ⭐️ - {v} р.", callback_data=f"stars|{k}"))

    keyboard.adjust(2)

    keyboard.row(InlineKeyboardButton(text=f"{btn.BACK}", callback_data="menu|balance"))

    return keyboard


def back_to_choose_star_count(stars_count: int) -> InlineKeyboardBuilder:
    """Назад к выбору количества звезд"""
    keyboard = InlineKeyboardBuilder()

    keyboard.row(InlineKeyboardButton(text=f"Оплатить {stars_count} ⭐️ ", pay=True))
    keyboard.row(InlineKeyboardButton(text=f"{btn.BACK}", callback_data="cancel_star_payment"))

    return keyboard