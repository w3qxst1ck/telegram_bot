import datetime
import uuid
from typing import Any

from aiogram import Router, types, F
from handlers.keyboards import buy as buy_kb
from database.orm import AsyncOrm
from schemas.connection import Connection
from handlers.messages import buy as ms
from cache import r
from settings import settings

router = Router()


@router.callback_query(F.data == "new_key")
async def new_key_menu_handler(callback: types.CallbackQuery, session: Any) -> None:
    """Покупка нового ключа"""
    tg_id = str(callback.from_user.id)

    # TODO test version
    user_with_conn = await AsyncOrm.get_user_with_connection_list(tg_id, session)

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

    msg = ms.new_key_message(user_with_conn.balance)
    await callback.message.edit_text(msg, reply_markup=buy_kb.new_key_keyboard().as_markup())


@router.callback_query(F.data.split("|")[0] == "new_key")
async def new_key_confirm_handler(callback: types.CallbackQuery, session: Any) -> None:
    """Подтверждение покупки нового ключа"""
    period = callback.data.split("|")[1]
    price = settings.price_list[period]
    tg_id = str(callback.from_user.id)

    # TODO test version
    user_with_conn = await AsyncOrm.get_user_with_connection_list(tg_id, session)

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

    # успешная покупка
    if user_with_conn.balance >= price:
        msg = ms.new_key_confirm_message(period)
        await callback.message.edit_text(msg, reply_markup=buy_kb.new_key_confirm_keyboard(period).as_markup())
    # недостаточно средств на балансе
    else:
        msg = ms.not_enough_balance_message(period, price, user_with_conn.balance)
        await callback.message.edit_text(msg, reply_markup=buy_kb.not_enough_balance_keyboard().as_markup())


@router.callback_query(F.data.split("|")[0] == "new_key_confirm")
async def new_key_create_handler(callback: types.CallbackQuery, session: Any) -> None:
    """Обработка подтверждения покупки нового ключа"""
    period = callback.data.split("|")[2]
    answer = callback.data.split("|")[1]
    price = settings.price_list[period]
    tg_id = str(callback.from_user.id)

    if answer == "no":
        await new_key_menu_handler(callback, session)
        return
    else:
        # TODO test version
        user_with_conn = await AsyncOrm.get_user_with_connection_list(tg_id, session)

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

        # подготовка нового Connection
        user_id = 1 # TODO поправить
        email = str(uuid.uuid4())
        key = "SOME KEY FOR TEST" # TODO поправить
        description = "SOME DESCRIPTION" # TODO поправить
        new_balance = user_with_conn.balance - price
        conn = Connection(
            user_id=user_id,
            tg_id=tg_id,
            active=True,
            start_date=datetime.datetime.now(),
            expire_date=datetime.datetime.now() + datetime.timedelta(days=int(period)*30),
            is_trial=False,
            email=email,
            key=key,
            description=description
        )
        # создание connection в бд
        await AsyncOrm.buy_new_key(conn, new_balance, session)
        # TODO выписать новый ключ
        # TODO списать с баланса деньги

        msg = ms.buy_new_key_message(period, price, conn.expire_date)
        await callback.message.edit_text(msg)