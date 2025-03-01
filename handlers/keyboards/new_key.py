from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from handlers.buttons import menu as btn
from settings import settings


def new_key_keyboard() -> InlineKeyboardBuilder:
    """Клавиатура для выбора период покупки нового ключа"""
    keyboard = InlineKeyboardBuilder()

    keyboard.row(
        InlineKeyboardButton(text=f"1 мес. ({settings.price_list['1']}р.)", callback_data="new_key_period|1"),
        InlineKeyboardButton(text=f"3 мес. ({settings.price_list['3']}р.)", callback_data="new_key_period|3")
    )
    keyboard.row(
        InlineKeyboardButton(text=f"6 мес. ({settings.price_list['6']}р.)", callback_data="new_key_period|6"),
        InlineKeyboardButton(text=f"12 мес. ({settings.price_list['12']}р.)", callback_data="new_key_period|12")
    )

    keyboard.row(InlineKeyboardButton(text=f"{btn.BACK}", callback_data="menu|buy"))

    return keyboard


def new_key_confirm_keyboard(period: str) -> InlineKeyboardBuilder:
    """Клавиатура для подтверждения покупки ключа"""
    keyboard = InlineKeyboardBuilder()

    keyboard.row(
        InlineKeyboardButton(text=f"Да", callback_data=f"new_key_confirm|{period}"),
        InlineKeyboardButton(text=f"Нет", callback_data=f"new_key")
    )

    return keyboard