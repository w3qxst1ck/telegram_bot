import datetime
import uuid
from typing import Any

from aiogram import Router, types, F
from aiogram.enums import ParseMode

from database.orm import AsyncOrm
from handlers.buttons import commands as cmd
from handlers.keyboards import menu as menu_kb
from schemas.connection import Server
from services import service
from utils.servers_load import get_less_loaded_server
from settings import settings
from logger import logger


TRIAL_KEY_DESCRIPTION = "🎁 Пробный"

router = Router()


@router.callback_query(F.data == "trial_key")
async def send_trial_key(message: types.CallbackQuery, session: Any) -> None:
    """Отправка пользователю ключа для пробного периода"""

    waiting_mess = await message.message.answer("Запрос выполняется...⏳")

    tg_id = str(message.from_user.id)
    already_has_trial = False
    trial_key = ""

    user_with_connections = await AsyncOrm.get_user_with_connection_list(tg_id, session, need_trial=True)

    # если уже использован пробный период
    if user_with_connections.trial_used:
        await message.message.answer("Вы уже использовали пробный период\n\n"
                                     f"Пополнить баланс и купить ключ вы можете в /{cmd.MENU[0]}",
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
        server_id: int = await get_less_loaded_server(session)
        server: Server = await AsyncOrm.get_server(server_id, session)

        # создаем ключ в панели 3x-ui пробный ключ
        new_uuid = str(uuid.uuid4())
        trial_key = await service.add_client(server, new_uuid, tg_id)

        # записываем в БД пробный ключ
        await AsyncOrm.create_connection(
            tg_id=tg_id,
            active=True,
            start_date=datetime.datetime.now(),
            expire_date=datetime.datetime.now() + datetime.timedelta(days=settings.trial_days),
            is_trial=True,
            email=new_uuid,
            key=trial_key,
            description=TRIAL_KEY_DESCRIPTION,
            server_id=server_id,
            session=session,
        )

    await waiting_mess.edit_text(
        "Ваш ключ, нажмите чтобы скопировать ⬇️\n\n"
        f"```{trial_key}```\n\n"
        f"Инструкцию по установке и настройке VPN вы можете посмотреть здесь /{cmd.INSTRUCTION[0]}",
        reply_markup=menu_kb.to_menu_keyboard().as_markup(),
        parse_mode=ParseMode.MARKDOWN
    )

    logger.info(f"Создан пробный коннект с ключом {trial_key} для пользователя {tg_id}")