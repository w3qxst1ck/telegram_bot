import os
from typing import Any

import aiogram
from aiogram import Router, types
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.deep_linking import decode_payload

from database.orm import AsyncOrm
from schemas.user import UserAdd
from handlers.buttons import commands as cmd
from handlers.buttons.menu import TRIAL_KEY
from handlers.users import main_menu
from settings import settings

router = Router()


@router.message(CommandStart(deep_link=True))
@router.message(Command(f"{cmd.START[0]}"))
async def start_handler(
        message: types.Message | types.CallbackQuery,
        admin: bool,
        state: FSMContext,
        command: CommandObject,
        bot: aiogram.Bot,
        session: Any) -> None:
    """Сообщение по команде /start"""

    tg_id: str = str(message.from_user.id)
    user_exists: bool = await AsyncOrm.check_user_already_exists(tg_id, session)

    args = command.args
    # если пользователь пришел по ссылке приглашению
    if args:
        # получаем телеграм id пользователя, который пригласил
        from_tg_id = decode_payload(args)

        # проверяем получал ли он уже бонус
        already_exist: bool = await AsyncOrm.is_users_ref_relation_exists(tg_id, session)

        # если записи не было создаем
        if not already_exist and not user_exists:
            await AsyncOrm.crete_users_ref_relation(tg_id, from_tg_id, session)

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

    await send_hello_message(message, admin, state, bot, session)


async def send_hello_message(message: types.Message, admin: bool, state: FSMContext, bot: aiogram.Bot, session: Any) -> None:
    """Стартовое сообщение"""
    name: str = message.from_user.first_name if message.from_user.first_name else message.from_user.username
    trial_used: bool = await AsyncOrm.get_trial_connection_status(str(message.from_user.id), session)

    msg = f"Привет, <b>{name}</b>!\n{settings.bot_name} предоставляет доступ к свободному интернету без " \
          f"ограничений!\n\n"

    # для пробного периода
    if not trial_used:
        msg += f"Вам доступен <b>бесплатный пробный период на {settings.trial_days} дней</b>.\n" \
               "Ваш ключ доступа ниже по кнопке\n\n" \
               f"Посмотреть свои ключи, профиль, пополнить баланс и купить ключ вы можете в /{cmd.MENU[0]}\n" \
               f"Инструкцию по установке vpn можно посмотреть по команде /{cmd.INSTRUCTION[0]}\n\n"

    # если пробный период уже истек
    else:
        msg += f"Посмотреть свои ключи, профиль, пополнить баланс и купить ключ вы можете в /{cmd.MENU[0]}\n" \
               f"Инструкцию по установке vpn можно посмотреть по команде /{cmd.INSTRUCTION[0]}\n\n"

    msg += f"Если у вас остались вопросы, вы можете обратиться в поддержку /{cmd.HELP[0]}"

    image_path = os.path.join("img", "start.jpg")
    if os.path.isfile(image_path):
        with open(image_path, "rb") as image_buffer:

            if not trial_used:
                keyboard = InlineKeyboardBuilder()
                keyboard.row(InlineKeyboardButton(text=f"{TRIAL_KEY}", callback_data=f"trial_key"))

                await message.answer_photo(
                    photo=BufferedInputFile(image_buffer.read(), filename="start.jpg"),
                    caption=msg,
                    reply_markup=keyboard.as_markup()
                )
            # если истек пробный период
            else:
                await message.answer_photo(
                    photo=BufferedInputFile(image_buffer.read(), filename="start.jpg"),
                    caption=msg,
                )
                await main_menu(message, admin, state, bot)


