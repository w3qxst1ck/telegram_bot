import datetime
import uuid
from typing import Any

from aiogram import Router, types, F
from aiogram.enums import ParseMode

from handlers.keyboards import new_key as kb
from handlers.keyboards.balance import not_enough_balance_keyboard
from handlers.keyboards.menu import to_menu_keyboard
from database.orm import AsyncOrm
from schemas.connection import Connection
from handlers.messages import new_key as ms
from handlers.messages.balance import not_enough_balance_message
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
    await callback.message.edit_text(msg, reply_markup=kb.new_key_keyboard().as_markup())


@router.callback_query(F.data.split("|")[0] == "new_key_period")
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

    # достаточно средств
    if user_with_conn.balance >= price:
        msg = ms.new_key_confirm_message(period, price)
        await callback.message.edit_text(msg, reply_markup=kb.new_key_confirm_keyboard(period).as_markup())
    # недостаточно средств на балансе
    else:
        msg = not_enough_balance_message(period, price, user_with_conn.balance)
        await callback.message.edit_text(msg, reply_markup=not_enough_balance_keyboard().as_markup())


@router.callback_query(F.data.split("|")[0] == "new_key_confirm")
async def new_key_create_handler(callback: types.CallbackQuery, session: Any) -> None:
    """Обработка подтверждения покупки нового ключа"""
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

    # подготовка нового Connection
    user_id = 1 # TODO поправить
    email = str(uuid.uuid4())
    # TODO поправить
    key = "vless://9ea0e3b8-c7f6-4224-92b1-631cee4aeaf5@somedomain123.store:443?type=tcp&security=reality&pbk=_V7Joja7EM0GukBFX7M_HBqtlJAz0hQuYIhoGqWVBwI&fp=chrome&sni=www.google.com&sid=6977dfdb8b9c54&spx=%2F#leva"
    description = "SOME DESCRIPTION" # TODO поправить
    new_balance = user_with_conn.balance - price
    server_id = 1 # TODO поправить
    new_conn = Connection(
        user_id=user_id,
        tg_id=tg_id,
        active=True,
        start_date=datetime.datetime.now(),
        expire_date=datetime.datetime.now() + datetime.timedelta(days=int(period)*30),
        is_trial=False,
        email=email,
        key=key,
        description=description,
        server_id=server_id
    )

    msg = ms.buy_new_key_message(period, price, new_conn.expire_date, new_balance, key)
    await callback.message.edit_text(msg, reply_markup=to_menu_keyboard().as_markup(), parse_mode=ParseMode.MARKDOWN)

    # создание connection в бд
    await AsyncOrm.buy_new_key(new_conn, new_balance, session)

    # TODO обновить кэш
    # user_with_conn.balance = new_balance
    # user_with_conn.connections.append(new_conn)
    # user_with_conn_json = user_with_conn.model_dump_json()
    # r.setex(f"profile:{tg_id}", 300, user_with_conn_json)
