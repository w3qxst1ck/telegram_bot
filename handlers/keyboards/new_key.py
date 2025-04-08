from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from handlers.buttons import menu as btn
from settings import settings
from handlers.buttons.regions import REGIONS


def new_key_country_keyboard(countries: list[str]) -> InlineKeyboardBuilder:
    """Клавиатура выбора страны"""
    keyboard = InlineKeyboardBuilder()

    for country in countries:
        country_with_flag = REGIONS[country]
        keyboard.row(InlineKeyboardButton(text=f"{country_with_flag}", callback_data=f"new_key_country|{country}"))

    keyboard.row(InlineKeyboardButton(text=f"{btn.BACK}", callback_data="menu|buy"))

    return keyboard


def new_key_keyboard(country: str) -> InlineKeyboardBuilder:
    """Клавиатура для выбора период покупки нового ключа"""
    keyboard = InlineKeyboardBuilder()

    keyboard.row(
        InlineKeyboardButton(text=f"1 мес. ({settings.price_list['1']}р.)", callback_data=f"new_key_period|1|{country}"),
        InlineKeyboardButton(text=f"3 мес. ({settings.price_list['3']}р.)", callback_data=f"new_key_period|3|{country}")
    )
    keyboard.row(
        InlineKeyboardButton(text=f"6 мес. ({settings.price_list['6']}р.)", callback_data=f"new_key_period|6|{country}"),
        InlineKeyboardButton(text=f"12 мес. ({settings.price_list['12']}р.)", callback_data=f"new_key_period|12|{country}")
    )

    keyboard.row(InlineKeyboardButton(text=f"{btn.BACK}", callback_data="new_key"))

    return keyboard


def new_key_confirm_keyboard(period: str, country: str) -> InlineKeyboardBuilder:
    """Клавиатура для подтверждения покупки ключа"""
    keyboard = InlineKeyboardBuilder()

    keyboard.row(
        InlineKeyboardButton(text=f"Да", callback_data=f"new_key_confirm|{period}|{country}"),
        InlineKeyboardButton(text=f"Нет", callback_data=f"new_key_country|{country}")
    )

    return keyboard


def skip_keyboard() -> InlineKeyboardBuilder:
    """Клавиатура для пропуска названия ключа"""
    keyboard = InlineKeyboardBuilder()

    keyboard.row(
        InlineKeyboardButton(text="Пропустить", callback_data=f"key_description")
    )

    return keyboard