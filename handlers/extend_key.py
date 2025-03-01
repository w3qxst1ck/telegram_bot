import datetime
import uuid
from typing import Any

from aiogram import Router, types, F
from handlers.keyboards import extend_key as kb
from database.orm import AsyncOrm
from schemas.connection import Connection
from handlers.messages import extend_key as ms
from handlers.messages.balance import not_enough_balance_message
from handlers.keyboards.balance import not_enough_balance_keyboard
from cache import r
from schemas.user import UserConnList
from settings import settings
from handlers.keyboards.menu import to_menu_keyboard

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
    await callback.message.edit_text(msg, reply_markup=kb.extend_key_menu_keyboard(user_with_conns).as_markup())


@router.callback_query(F.data.split("|")[0] == "extend_key_email")
async def extend_key_period_handler(callback: types.CallbackQuery, session: Any) -> None:
    """Выбор периода при продлении ключа"""
    tg_id = str(callback.from_user.id)
    email = callback.data.split("|")[1]

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

    # TODO добавить кэш
    conn = await AsyncOrm.get_connection(email, session)

    msg = ms.extend_key_period_message(user_with_conns.balance, email, conn.active, conn.expire_date)
    await callback.message.edit_text(msg, reply_markup=kb.extend_key_period_keyboard(email).as_markup())


@router.callback_query(F.data.split("|")[0] == "extend_key_period")
async def extend_key_confirm_handler(callback: types.CallbackQuery, session: Any) -> None:
    """Запрос подтверждения о продлении"""
    tg_id = str(callback.from_user.id)
    period = callback.data.split("|")[1]
    email = callback.data.split("|")[2]
    price = settings.price_list[period]

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

    # достаточно средств
    if user_with_conns.balance >= price:
        msg = ms.extend_key_confirm_message(period, email, price)
        await callback.message.edit_text(msg, reply_markup=kb.extend_key_confirm_keyboard(period, email).as_markup())
    # недостаточно средств на балансе
    else:
        msg = not_enough_balance_message(period, price, user_with_conns.balance)
        await callback.message.edit_text(msg, reply_markup=not_enough_balance_keyboard().as_markup())


@router.callback_query(F.data.split("|")[0] == "extend_key_confirm")
async def extend_key_handler(callback: types.CallbackQuery, session: Any) -> None:
    """Обработка подтверждения продления ключа"""
    tg_id = str(callback.from_user.id)
    period = callback.data.split("|")[1]
    email = callback.data.split("|")[2]
    price = settings.price_list[period]

    # TODO test version
    user_with_conns = await AsyncOrm.get_user_with_connection_list(tg_id, session)

    # TODO prod version
    # cached_data = r.get(f"profile:{tg_id}")
    # if cached_data:
    #     # from cache
    #     user_with_conn = UserConnList.model_validate_json(cached_data)
    # else:
    #     # from DB
    #     user_with_conn = await AsyncOrm.get_user_with_connection_list(tg_id, session)
    #     user_with_conn_json = user_with_conn.model_dump_json()
    #     r.setex(f"profile:{tg_id}", 300, user_with_conn_json)

    # подготовка данных для обновления connection
    # TODO добавить кэш
    conn = await AsyncOrm.get_connection(email, session)

    if conn.expire_date >= datetime.datetime.now():
        new_expire_date = conn.expire_date + datetime.timedelta(days=int(period)*30)
    else:
        new_expire_date = datetime.datetime.now() + datetime.timedelta(days=int(period)*30)

    new_balance = user_with_conns.balance - price

    # отправка сообщения
    msg = ms.extend_key_message(period, price, new_expire_date, email, new_balance)
    await callback.message.edit_text(msg, reply_markup=to_menu_keyboard().as_markup())

    # внесение изменений в БД
    await AsyncOrm.extend_key(email, new_expire_date, tg_id, new_balance, session)
    # TODO обновить кэш
    # user_with_conns = await AsyncOrm.get_user_with_connection_list(tg_id, session)
    # user_with_conn_json = user_with_conns.model_dump_json()
    # r.setex(f"profile:{tg_id}", 300, user_with_conn_json)


