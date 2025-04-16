import datetime
import time

from aiogram import Router, F
from aiogram import types
from typing import Any

from aiogram.enums import ParseMode
from aiogram.filters import Command

from database.orm import AsyncOrm
from cache import r
from schemas.user import UserConnList
from handlers.messages.keys import keys_message
from handlers.keyboards import keys as kb
from handlers.buttons import commands as cmd
from services.service import get_client_traffic_for_all_keys


router = Router()


@router.callback_query(F.data.split("|")[1] == "keys")
@router.message(Command(cmd.KEYS[0]))
async def profile(message: types.Message | types.CallbackQuery, session: Any):
    """Карточка профиля с ключами"""

    tg_id = str(message.from_user.id)

    # todo test version
    if type(message) == types.Message:
        waiting_msg = await message.answer("Запрос выполняется...⏳")
    else:
        await message.message.edit_text("Запрос выполняется...⏳")

    # todo prod version
    cached_data = r.get(f"user_conn_server:{tg_id}")
    if cached_data:
        # from cache
        user_with_conn = UserConnList.model_validate_json(cached_data)
    else:
        # from DB
        user_with_conn = await AsyncOrm.get_user_with_connection_list(tg_id, session)

        # получение трафика
        user_with_conn.connections = await get_client_traffic_for_all_keys(user_with_conn.connections, session)

    msg = keys_message(user_with_conn)

    if type(message) == types.Message:
        await waiting_msg.edit_text(
            msg,
            reply_markup=kb.keys_keyboard().as_markup(),
            parse_mode=ParseMode.MARKDOWN
        )
    elif type(message) == types.CallbackQuery:
        await message.message.edit_text(
            msg,
            reply_markup=kb.keys_keyboard(back_btn=True).as_markup(),
            parse_mode=ParseMode.MARKDOWN
        )

    # добавление данных в кэш
    if not cached_data:
        # user to json (str) for redis storing
        user_with_conn_json = user_with_conn.model_dump_json()
        r.setex(f"user_conn_server:{tg_id}", 300, user_with_conn_json)
