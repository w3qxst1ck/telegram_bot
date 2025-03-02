from typing import Any
import datetime

import aiogram
import asyncpg

from database.orm import AsyncOrm
from logger import logger
from schemas.connection import Server
from settings import settings
from services import service


async def run_every_hour() -> None:
    """Выполняется каждый час"""
    session = await asyncpg.connect(
        user=settings.db.postgres_user,
        host=settings.db.postgres_host,
        password=settings.db.postgres_password,
        port=settings.db.postgres_port,
        database=settings.db.postgres_db
    )
    try:
        await off_expired_connections(session)
        # TODO раз в час сюда

    finally:
        await session.close()


async def off_expired_connections(session: Any):
    """Проверяет активность подписок"""
    all_connections = await AsyncOrm.get_active_connections(session)

    for conn in all_connections:
        # TODO разобраться с time zones
        print(f"expire: {conn.expire_date}")
        print(f"now: {datetime.datetime.now()}")

        if conn.expire_date < datetime.datetime.now():

            # если ключ пробный - удаляем его
            if conn.is_trial:
                server: Server = await AsyncOrm.get_server(conn.server_id, session)
                # удаление в панели
                await service.delete_client(server, conn.email)
                # удаление в БД
                await AsyncOrm.delete_connection(conn.email, session)
                # TODO оповестить пользователя
                continue

            # переводим подписку в неактивные в БД
            await AsyncOrm.deactivate_connection(conn.email, session)

            # блокируем ключ в панели
            server: Server = await AsyncOrm.get_server(conn.server_id, session)
            await service.block_client(server, conn.email, conn.tg_id)

            # TODO оповестить пользователя


