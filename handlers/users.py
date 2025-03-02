import datetime
import uuid
from typing import Any

from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.enums import ParseMode

from database.orm import AsyncOrm
from handlers.buttons import commands as cmd
from handlers.keyboards import menu as menu_kb
from services import service
from settings import settings
from utils.servers_load import get_less_loaded_server

router = Router()


@router.message(Command(f"{cmd.INSTRUCTION[0]}"))
async def instruction_handler(message: types.Message) -> None:
    # TODO не потерять (копирование текста по нажатию)
    await message.answer("`Instruction message`", parse_mode=ParseMode.MARKDOWN_V2)


@router.message(Command(f"{cmd.HELP[0]}"))
async def help_handler(message: types.Message) -> None:
    await message.answer("Help message")


@router.message(Command(f"{cmd.MENU[0]}"))
@router.callback_query(F.data == "menu")
async def main_menu(message: types.Message | types.CallbackQuery, admin: bool) -> None:
    """Отправка приветственного сообщения"""
    name: str = message.from_user.first_name if message.from_user.first_name else message.from_user.username

    msg = f"Рады видеть тебя, <b>{name}</b>!\n\n" \
          f"Пополняйте баланс и оформляйте подписку для доступа к VPN"

    if type(message) == types.Message:
        await message.answer(msg, reply_markup=menu_kb.main_menu_keyboard(admin).as_markup())
    else:
        await message.message.edit_text(msg, reply_markup=menu_kb.main_menu_keyboard(admin).as_markup())


@router.callback_query(F.data == "trial_key")
async def send_trial_key(message: types.CallbackQuery, session: Any) -> None:
    """Отправка пользователю ключа для пробного периода"""
    tg_id = str(message.from_user.id)
    already_has_trial = False
    trial_key = ""

    user_with_connections = await AsyncOrm.get_user_with_connection_list(tg_id, session, need_trial=True)

    # если уже использован пробный период
    if user_with_connections.trial_used:
        await message.message.answer("Вы уже использовали пробный период\n\n"
                                     f"Пополнить баланс и купить подписку вы можете в /{cmd.MENU[0]}",
                                     reply_markup=menu_kb.to_menu_keyboard().as_markup())
        return

    # проверяем наличие пробного ключа у пользователя
    for conn in user_with_connections.connections:
        # если есть действующий ключ пробный, возвращаем его
        if conn.is_trial:
            already_has_trial = True
            trial_key = conn.key

    # пользователь еще не использовал пробный ключ и в connections его еще нет
    if not already_has_trial and not user_with_connections.trial_used:
        server_id = await get_less_loaded_server(session)
        server = await AsyncOrm.get_server(server_id, session)

        # создаем ключ в панели 3x-ui пробный ключ
        new_uuid = str(uuid.uuid4())
        trial_key = await service.add_client(server, new_uuid, tg_id)

        # записываем в базу данных пробный ключ
        await AsyncOrm.create_connection(
            tg_id=tg_id,
            active=True,
            start_date=datetime.datetime.now(),
            expire_date=datetime.datetime.now() + datetime.timedelta(days=1),
            is_trial=True,
            email=new_uuid,
            key=trial_key,
            description=None,
            server_id=server_id,
            session=session,
        )

    await message.message.answer(
        "Ваш ключ, нажмите чтобы скопировать ⬇️\n\n"
        f"```{trial_key}```\n\n"
        f"Инструкцию по установке и настройке VPN вы можете посмотреть здесь /{cmd.INSTRUCTION[0]}",
        reply_markup=menu_kb.to_menu_keyboard().as_markup(),
        parse_mode=ParseMode.MARKDOWN
    )