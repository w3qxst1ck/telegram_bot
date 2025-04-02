from typing import Any
import datetime

import aiogram
import asyncpg
from aiogram.enums import ParseMode

from database.orm import AsyncOrm
from logger import logger
from schemas.connection import Server, ConnServerScheduler
from settings import settings
from services import service
from handlers.messages import scheduler as msg


async def run_every_hour(bot: aiogram.Bot) -> None:
    """Выполняется каждый час"""
    session = await asyncpg.connect(
        user=settings.db.postgres_user,
        host=settings.db.postgres_host,
        password=settings.db.postgres_password,
        port=settings.db.postgres_port,
        database=settings.db.postgres_db
    )

    try:
        # TODO раз в час сюда
        await off_expired_connections(session, bot)
        await check_traffic_excess(session, bot)

    except Exception:
        # TODO добавить логи на выполнение шедулеров
        pass

    finally:
        await session.close()


async def off_expired_connections(session: Any, bot: aiogram.Bot):
    """
    Проверяет активность подписок, если expire_date истек - блокирует ключ,
    если истекший ключ - пробный, он удаляется
    """
    all_connections = await AsyncOrm.get_active_connections(session)

    for conn in all_connections:
        # TODO разобраться с time zones
        if conn.expire_date < datetime.datetime.now():

            # если ключ пробный - удаляем его
            if conn.is_trial:
                server: Server = await AsyncOrm.get_server(conn.server_id, session)

                # удаление в панели
                await service.delete_client(server, conn.email)

                # удаление в БД
                await AsyncOrm.delete_connection(conn.email, session)

                # перевод trial_used в True у пользователя
                await AsyncOrm.set_trial_used_true(conn.tg_id, session)

                # оповещение пользователя
                message = msg.expire_trial_key(conn.key)
                await bot.send_message(conn.tg_id, message, parse_mode=ParseMode.MARKDOWN)

            # для обычных ключей
            else:
                # переводим connection в неактивные в БД
                await AsyncOrm.deactivate_connection(conn.email, session)

                # блокируем ключ в панели
                server: Server = await AsyncOrm.get_server(conn.server_id, session)
                await service.block_client(server, conn.email, conn.tg_id)

                # оповещение пользователя
                message = msg.expire_key(conn)
                await bot.send_message(conn.tg_id, message, parse_mode=ParseMode.MARKDOWN)


async def check_traffic_excess(session: Any, bot: aiogram.Bot) -> None:
    """Проверяет превышение трафика пользователей и блокирует, тех кто превысил"""
    active_connections: list[ConnServerScheduler] = await AsyncOrm.get_connections_with_servers(session)

    for conn in active_connections:
        current_traffic: float = await service.get_client_traffic(conn.api_url, conn.email)

        if current_traffic > settings.traffic_limit:
            # TODO проблема в блокировке ключа (нужно чтобы она отличалась от блокировки по дате)
            # блокируем ключ в панели
            # server: Server = await AsyncOrm.get_server(conn.server_id, session)


            # TODO оповестить пользователя
            pass



