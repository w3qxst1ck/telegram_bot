import datetime
import os
from typing import Any

import asyncpg
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import BufferedInputFile

from database.orm import AsyncOrm
from schemas.user import UserAdd
from handlers.buttons import commands as cmd
from handlers.users import main_menu
from settings import settings

router = Router()


@router.message(Command(f"{cmd.START[0]}"))
async def start_handler(message: types.Message | types.CallbackQuery, admin:bool, session: Any) -> None:
    """Сообщение по команде /start"""
    tg_id: str = str(message.from_user.id)

    await create_user_if_not_exists(tg_id, message, session)
    await send_hello_message(message, session)
    await main_menu(message, admin)


async def send_hello_message(message: types.Message, session: Any) -> None:
    """Стартовое сообщение"""
    name: str = message.from_user.first_name if message.from_user.first_name else message.from_user.username
    trial_status: asyncpg.Record = await AsyncOrm.get_trial_subscription_status(str(message.from_user.id), session)
    image_path = os.path.join("img", "start.png")

    msg = f"Привет, <b>{name}</b>!\n{settings.bot_name} предоставляет доступ к свободному интернету без " \
              f"ограничений!\n\n"

    # для пробного периода
    if trial_status["is_trial"] and not trial_status["trial_used"]:
        trial_key = "123456789"  # TODO добавить таблицу ключей и получить его тут
        msg += f"Вам доступен бесплатный пробный период на <b>{settings.trial_days} день</b>.\n" \
                   f"Ваш ключ доступа:\n<b>{trial_key}</b>\n\n" \
                   f"Инструкцию по установке vpn можно посмотреть по команде /{cmd.INSTRUCTION[0]}\n\n"

    # если пробный период уже истек
    else:
        msg += f"Ваш пробный период истек :(\nВы можете пополнить баланс своего профиля /{cmd.BALANCE[0]} и " \
                   f"приобрести <b>ключ доступа по команде /{cmd.BUY[0]}</b>\n\n"

    msg += f"Если у вас остались вопросы, вы можете обратиться в поддержку /{cmd.HELP[0]}"

    if os.path.isfile(image_path):
        with open(image_path, "rb") as image_buffer:
            if type(message) == types.Message:
                await message.answer_photo(
                    photo=BufferedInputFile(image_buffer.read(), filename="start.png"),
                    caption=msg,
                )
    else:
        await message.answer(msg)


async def create_user_if_not_exists(tg_id: str, message: types.Message, session: Any) -> None:
    """Создает пользователя в БД, если он не зарегистрирован"""
    user_exists: bool = await AsyncOrm.check_user_already_exists(tg_id, session)

    if not user_exists:
        user: UserAdd = UserAdd(
            tg_id=tg_id,
            username=message.from_user.username,
            firstname=message.from_user.first_name,
            lastname=message.from_user.last_name
        )
        await AsyncOrm.create_user(user, session)

        # создаем подписку сразу с пробным периодом на 1 день
        await AsyncOrm.create_subscription(
            tg_id=tg_id,
            active=True,
            start_date=datetime.datetime.now(),
            expire_date=datetime.datetime.now() + datetime.timedelta(days=settings.trial_days),
            is_trial=True,
            trial_used=False,
            session=session
        )



