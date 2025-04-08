import datetime
import uuid
from typing import Any

from aiogram import Router, types, F
from handlers.keyboards import extend_key as kb
from database.orm import AsyncOrm
from schemas.connection import Connection, ConnectionServer
from handlers.messages import extend_key as ms
from handlers.messages import errors as err_ms
from handlers.messages.balance import not_enough_balance_message
from handlers.keyboards.balance import not_enough_balance_extend_key_keyboard
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

    # TODO test version
    conn_server = await AsyncOrm.get_connection_server(email, session)

    # TODO prod version
    # cached_data = r.get(f"conn_server:{email}")
    # if cached_data:
    #     # from cache
    #     conn_server = ConnectionServer.model_validate_json(cached_data)
    # else:
    #     # from DB
    #     conn_server = await AsyncOrm.get_connection_server(email, session)
    #     conn_server_json = conn_server.model_dump_json()
    #     r.setex(f"extend_key:{tg_id}", 100, conn_server_json)

    msg = ms.extend_key_period_message(user_with_conns.balance, conn_server.description, conn_server.active,
                                       conn_server.expire_date, conn_server.region)
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

    # TODO test version
    conn_server = await AsyncOrm.get_connection_server(email, session)

    # TODO prod version
    # cached_data = r.get(f"conn_server:{email}")
    # if cached_data:
    #     # from cache
    #     conn_server = ConnectionServer.model_validate_json(cached_data)
    # else:
    #     # from DB
    #     conn_server = await AsyncOrm.get_connection_server(email, session)
    #     conn_server_json = conn_server.model_dump_json()
    #     r.setex(f"extend_key:{tg_id}", 100, conn_server_json)

    # достаточно средств
    if user_with_conns.balance >= price:
        msg = ms.extend_key_confirm_message(period, conn_server.description, price, conn_server.region)
        await callback.message.edit_text(msg, reply_markup=kb.extend_key_confirm_keyboard(period, email).as_markup())
    # недостаточно средств на балансе
    else:
        msg = not_enough_balance_message(period, price, user_with_conns.balance)
        await callback.message.edit_text(msg, reply_markup=not_enough_balance_extend_key_keyboard(email).as_markup())


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
    # TODO test version
    conn_server = await AsyncOrm.get_connection_server(email, session)

    # TODO prod version
    # cached_data = r.get(f"conn_server:{email}")
    # if cached_data:
    #     # from cache
    #     conn_server = ConnectionServer.model_validate_json(cached_data)
    # else:
    #     # from DB
    #     conn_server = await AsyncOrm.get_connection_server(email, session)
    #     conn_server_json = conn_server.model_dump_json()
    #     r.setex(f"extend_key:{tg_id}", 100, conn_server_json)

    # ключ еще не просрочен (не меняем start_date)
    if conn_server.expire_date >= datetime.datetime.now():
        new_expire_date = conn_server.expire_date + datetime.timedelta(days=int(period)*30)
        new_start_date = conn_server.start_date
    # просроченный ключ (start_date = now)
    else:
        new_expire_date = datetime.datetime.now() + datetime.timedelta(days=int(period)*30)
        new_start_date = datetime.datetime.now()

    new_balance = user_with_conns.balance - price

    try:
        # внесение изменений в БД
        await AsyncOrm.extend_key(email, new_start_date, new_expire_date, tg_id, new_balance, session)

        # отправка сообщения
        msg = ms.extend_key_message(period, price, new_expire_date, conn_server.description, new_balance, conn_server.region)
        await callback.message.edit_text(msg, reply_markup=to_menu_keyboard().as_markup())

        # TODO обновить кэш
        # user_with_conns = await AsyncOrm.get_user_with_connection_list(tg_id, session)
        # user_with_conn_json = user_with_conns.model_dump_json()
        # r.setex(f"profile:{tg_id}", 300, user_with_conn_json)

        # conn_server_json = conn_server.model_dump_json()
        # r.setex(f"extend_key:{tg_id}", 100, conn_server_json)

    except Exception:
        error_msg = err_ms.error_msg()
        await callback.message.edit_text(error_msg, reply_markup=to_menu_keyboard().as_markup())
