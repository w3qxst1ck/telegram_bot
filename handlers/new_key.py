import datetime
import uuid
from typing import Any

from aiogram import Router, types, F
from aiogram.enums import ParseMode

from handlers.buttons.commands import HELP
from handlers.keyboards import new_key as kb
from handlers.keyboards.balance import not_enough_balance_keyboard
from handlers.keyboards.menu import to_menu_keyboard
from database.orm import AsyncOrm
from schemas.connection import Connection, Server
from handlers.messages import new_key as ms
from handlers.messages.balance import not_enough_balance_message
from services.service import add_client
from cache import r
from settings import settings
from utils.servers_load import get_less_loaded_server

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
    # исключение двойного нажатия
    await callback.message.edit_text("Запрос выполняется...⏳")

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

    # добавление клиента в панель
    server_id = await get_less_loaded_server(session)
    server: Server = await AsyncOrm.get_server(server_id, session)
    email = str(uuid.uuid4())
    key = await add_client(server, email, tg_id)

    # подготовка нового Connection
    description = "SOME DESCRIPTION"    # TODO поправить
    new_balance = user_with_conn.balance - price
    new_conn = Connection(
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

    # создание connection в бд
    try:
        await AsyncOrm.buy_new_key(new_conn, new_balance, session)
        msg = ms.buy_new_key_message(period, price, new_conn.expire_date, new_balance, key)
        await callback.message.edit_text(msg, reply_markup=to_menu_keyboard().as_markup(), parse_mode=ParseMode.MARKDOWN)

    except Exception:
        error_msg = f"😕 Что-то пошло не так...\n\nДеньги с баланса списаны не будут. Попробуйте повторить запрос позже. " \
                    f"При повторном возникновении ошибки обратитесь к администрации с помощью команды /{HELP[0]}"
        await callback.message.edit_text(error_msg, reply_markup=to_menu_keyboard().as_markup())

    # TODO обновить кэш
    # user_with_conn.balance = new_balance
    # user_with_conn.connections.append(new_conn)
    # user_with_conn_json = user_with_conn.model_dump_json()
    # r.setex(f"profile:{tg_id}", 300, user_with_conn_json)
