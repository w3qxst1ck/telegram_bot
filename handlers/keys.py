import datetime
import time

from aiogram import Router, F
from aiogram import types
from typing import Any

from aiogram.enums import ParseMode
from aiogram.filters import Command

from database.orm import AsyncOrm
from handlers.messages.keys import keys_message
from cache import r
from schemas.user import UserConnList
from handlers.keyboards import keys as kb
from handlers.buttons import commands as cmd
from services.service import get_client_traffic, get_client_traffic_for_all_keys

router = Router()


@router.callback_query(F.data.split("|")[1] == "keys")
@router.message(Command(cmd.KEYS[0]))
async def profile(message: types.Message | types.CallbackQuery, session: Any):
    """Карточка профиля с ключами"""
    tg_id = str(message.from_user.id)

    start = time.time()

    # todo test version
    user_with_conn = await AsyncOrm.get_user_with_connection_list(tg_id, session)

    # FAST VERSION 2.55
    user_with_conn.connections = await get_client_traffic_for_all_keys(user_with_conn.connections, session)

    # SLOW VERSION 5.11
    # conns_with_traffic = []
    # for conn in user_with_conn.connections:
    #     server = await AsyncOrm.get_server(conn.server_id, session)
    #     traffic = await get_client_traffic(server, conn.email)
    #     conn.traffic = traffic
    #     conns_with_traffic.append(conn)
    # user_with_conn.connections = conns_with_traffic

    # todo prod version
    # cached_data = r.get(f"profile:{tg_id}")
    # if cached_data:
    #     # from cache
    #     user_with_conn = UserConnList.model_validate_json(cached_data)
    # else:
    #     # from DB
    #     user_with_conn = await AsyncOrm.get_user_with_connection_list(tg_id, session)
    #
    #     # получение трафика
    #     # TODO что-то сделать со временем выполнения c FAST VERSION
    #     conns_with_traffic = []
    #     for conn in user_with_conn.connections:
    #         server = await AsyncOrm.get_server(conn.server_id, session)
    #         traffic = await get_client_traffic(server, conn.email)
    #         conn.traffic = traffic
    #         conns_with_traffic.append(conn)
    #     user_with_conn.connections = conns_with_traffic
    #
    #     # user to json (str) for redis storing
    #     user_with_conn_json = user_with_conn.model_dump_json()
    #     r.setex(f"profile:{tg_id}", 300, user_with_conn_json)

    msg = keys_message(user_with_conn)

    if type(message) == types.Message:
        await message.answer(
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

    end = time.time()
    print(end - start)

