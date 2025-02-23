import os
from typing import Any

import asyncpg
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import BufferedInputFile, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.orm import AsyncOrm
from schemas.user import UserAdd
from handlers.buttons import commands as cmd
from handlers.buttons.menu import TRIAL_KEY
from handlers.users import main_menu
from settings import settings

router = Router()


@router.message(Command(f"{cmd.START[0]}"))
async def start_handler(message: types.Message | types.CallbackQuery, admin: bool, session: Any) -> None:
    """Сообщение по команде /start"""
    tg_id: str = str(message.from_user.id)

    await create_user_if_not_exists(tg_id, message, session)
    await send_hello_message(message, admin, session)


async def send_hello_message(message: types.Message, admin: bool, session: Any) -> None:
    """Стартовое сообщение"""
    name: str = message.from_user.first_name if message.from_user.first_name else message.from_user.username
    trial_status: bool = await AsyncOrm.get_trial_subscription_status(str(message.from_user.id), session)

    msg = f"Привет, <b>{name}</b>!\n{settings.bot_name} предоставляет доступ к свободному интернету без " \
          f"ограничений!\n\n"

    # для пробного периода
    if not trial_status:
        msg += f"Вам доступен <b>бесплатный пробный период на {settings.trial_days} день</b>.\n" \
               "Ваш ключ доступа ниже по кнопке\n\n" \
               f"Посмотреть свои ключи, профиль, пополнить баланс и купить подписку вы можете в /{cmd.MENU[0]}\n" \
               f"Инструкцию по установке vpn можно посмотреть по команде /{cmd.INSTRUCTION[0]}\n\n"

    # если пробный период уже истек
    else:
        msg += f"Посмотреть свои ключи, профиль, пополнить баланс и купить подписку вы можете в /{cmd.MENU[0]}\n" \
               f"Инструкцию по установке vpn можно посмотреть по команде /{cmd.INSTRUCTION[0]}\n\n"

    msg += f"Если у вас остались вопросы, вы можете обратиться в поддержку /{cmd.HELP[0]}"

    image_path = os.path.join("img", "start.png")
    if os.path.isfile(image_path):
        with open(image_path, "rb") as image_buffer:

            if not trial_status:
                keyboard = InlineKeyboardBuilder()
                keyboard.row(InlineKeyboardButton(text=f"{TRIAL_KEY}", callback_data=f"trial_key"))

                await message.answer_photo(
                    photo=BufferedInputFile(image_buffer.read(), filename="start.png"),
                    caption=msg,
                    reply_markup=keyboard.as_markup()
                )
            # если истек пробный период
            else:
                await message.answer_photo(
                    photo=BufferedInputFile(image_buffer.read(), filename="start.png"),
                    caption=msg,
                )
                await main_menu(message, admin)


async def create_user_if_not_exists(tg_id: str, message: types.Message, session: Any) -> None:
    """Создает пользователя в БД, если он не зарегистрирован"""
    user_exists: bool = await AsyncOrm.check_user_already_exists(tg_id, session)

    if not user_exists:
        user: UserAdd = UserAdd(
            tg_id=tg_id,
            username=message.from_user.username,
            firstname=message.from_user.first_name,
            lastname=message.from_user.last_name,
            balance=0,
            trial_used=False
        )
        await AsyncOrm.create_user(user, session)



