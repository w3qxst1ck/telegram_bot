import datetime
import uuid
from typing import Any

from aiogram import Router, types, F
from handlers.keyboards import buy as buy_kb
from database.orm import AsyncOrm
from schemas.connection import Connection
from handlers.messages import buy as ms
from cache import r
from schemas.user import UserConnList
from settings import settings

router = Router()


@router.callback_query(F.data == "extend_key")
async def extend_key_menu_handler(callback: types.CallbackQuery, session: Any) -> None:
    """Меню продления ключа"""
    tg_id = str(callback.from_user.id)

    # TODO test version
    user_with_conns = await AsyncOrm.get_user_with_connection_list(tg_id, session, need_trial=False)

    # TODO prod version
    # cached_data = r.get(f"extend_key:{tg_id}")
    # if cached_data:
    #     # from cache
    #     user_with_conn = UserConnList.model_validate_json(cached_data)
    # else:
    #     # from DB
    #     user_with_conn = await AsyncOrm.get_user_with_connection_list(tg_id, session, need_trial=False)
    #     user_with_conn_json = user_with_conn.model_dump_json()
    #     r.setex(f"extend_key:{tg_id}", 300, user_with_conn_json)

    msg = ms.extend_key_menu_message(user_with_conns)
    await callback.message.edit_text(msg, reply_markup=buy_kb.extend_key_menu_keyboard(user_with_conns).as_markup())


@router.callback_query(F.data.split("|")[0] == "extend_key_period")
async def extend_key_period_handler(callback: types.CallbackQuery, session: Any) -> None:
    """Выбор периода при продления ключа"""
    pass
