import datetime

from typing import Any

from aiogram import Router, F
from aiogram import types

from cache import r
import handlers.messages.extra_traffic as ms
from handlers.messages.errors import general_error_msg
from handlers.messages.balance import not_enough_money
from database.orm import AsyncOrm
from handlers.keyboards import extra_traffic as kb
from handlers.keyboards.menu import to_menu_keyboard
from schemas.connection import ConnectionRegion, Connection, Server
from settings import settings
from services.service import refresh_client_current_traffic

from logger import logger

router = Router()


@router.callback_query(F.data == "buy-extra-traffic")
async def buy_extra_traffic_menu(callback: types.CallbackQuery, session: Any):
    """Меню выбора ключей для покупки дополнительного трафика"""
    tg_id = str(callback.from_user.id)
    active_connections: list[ConnectionRegion] = await AsyncOrm.get_active_user_connections(tg_id, session)

    is_empty: bool = len(active_connections) == 0
    msg = ms.buy_extra_traffic_message(is_empty)

    await callback.message.edit_text(msg, reply_markup=kb.keys_list(active_connections).as_markup())


@router.callback_query(F.data.split("|")[0] == "extra-traffic")
async def buy_extra_traffic(callback: types.CallbackQuery, session: Any):
    """Покупка доп. трафика для ключа"""
    conn_id = int(callback.data.split("|")[1])
    tg_id = str(callback.from_user.id)

    connection: Connection = await AsyncOrm.get_connection_by_id(conn_id, session)
    server: Server = await AsyncOrm.get_server(connection.server_id, session)
    user_balance: int = await AsyncOrm.get_user_balance(tg_id, session)

    msg = ms.confirm_buy_extra_traffic(connection, server.region, user_balance)

    await callback.message.edit_text(msg, reply_markup=kb.confirm_keyboard(conn_id).as_markup())


@router.callback_query(F.data.split("|")[0] == "confirm_buy")
async def confirm_buy_extra_traffic(callback: types.CallbackQuery, session: Any):
    """Подтверждение покупки доп. трафика"""
    waiting_mess = await callback.message.edit_text("Запрос выполняется...⏳")

    conn_id = int(callback.data.split("|")[1])
    tg_id = str(callback.from_user.id)

    connection: Connection = await AsyncOrm.get_connection_by_id(conn_id, session)
    user_balance: int = await AsyncOrm.get_user_balance(tg_id, session)
    server: Server = await AsyncOrm.get_server(connection.server_id, session)

    # если достаточно денег
    if user_balance >= settings.extra_traffic_price:

        try:
            # обновить трафик
            await refresh_client_current_traffic(server, connection.email)

            # уменьшаем баланс
            await AsyncOrm.decrease_balance_on_amount(tg_id, settings.extra_traffic_price, session)

            # оповещаем пользователя
            msg = ms.success_buy_extra_traffic(connection, server.region)
            await waiting_mess.edit_text(msg, reply_markup=to_menu_keyboard().as_markup())

            # создаем платеж в payments
            await AsyncOrm.create_payment(
                tg_id,
                settings.extra_traffic_price,
                f"TRAF_{conn_id}",
                True,
                datetime.datetime.now(),
                session
            )

            # удаляем кэш
            r.delete(f"user_conn_server:{tg_id}")

            logger.info(f"Обнулен трафик ключа id: {conn_id} email: {connection.email} пользователя {tg_id}")

        except Exception as e:
            msg = general_error_msg()
            await waiting_mess.edit_text(msg, reply_markup=to_menu_keyboard().as_markup())
            logger.error(f"Не удалось обновить трафик ключа id {conn_id} пользователю {tg_id}: {e}")

    # недостаточно средств
    else:
        msg = not_enough_money(settings.extra_traffic_price, user_balance)
        await waiting_mess.edit_text(msg, reply_markup=to_menu_keyboard().as_markup())




