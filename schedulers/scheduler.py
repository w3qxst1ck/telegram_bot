from typing import Any
import datetime

import aiogram
import asyncpg
from aiogram.enums import ParseMode

from database.orm import AsyncOrm
from logger import logger
from schemas.connection import Server
from schemas.referrals import Referrals
from services import service
from handlers.messages import scheduler as ms
from settings import settings


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
        await off_expired_connections(session, bot)
        await check_ref_links_and_add_bonus(session, bot)

    except Exception as e:
        logger.error(f"Ошибка при выполнении шедулера (1 раз в час) {e}")

    finally:
        await session.close()


async def run_every_day(bot: aiogram.Bot) -> None:
    """Выполняется 1 раз в день"""
    session = await asyncpg.connect(
        user=settings.db.postgres_user,
        host=settings.db.postgres_host,
        password=settings.db.postgres_password,
        port=settings.db.postgres_port,
        database=settings.db.postgres_db
    )

    try:
        await refresh_current_traffic(session, bot)

    except Exception as e:
        logger.error(f"Ошибка при выполнении шедулера (1 раз в день) {e}")

    finally:
        await session.close()


async def off_expired_connections(session: Any, bot: aiogram.Bot) -> None:
    """
    Проверяет активность подписок, если expire_date истек - блокирует ключ,
    если истекший ключ - пробный, он удаляется
    """
    active_connections = await AsyncOrm.get_active_connections(session)

    for conn in active_connections:
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
                message = ms.expire_trial_key(conn.key)
                await bot.send_message(conn.tg_id, message, parse_mode=ParseMode.MARKDOWN)

            # для обычных ключей
            else:
                # переводим connection в неактивные в БД
                await AsyncOrm.deactivate_connection(conn.email, session)

                # блокируем ключ в панели
                server: Server = await AsyncOrm.get_server(conn.server_id, session)
                await service.block_client(server, conn.email, conn.tg_id)

                # оповещение пользователя
                message = ms.expire_key(conn)
                await bot.send_message(conn.tg_id, message, parse_mode=ParseMode.MARKDOWN)


async def check_ref_links_and_add_bonus(session: Any, bot: aiogram.Bot) -> None:
    """Начисляет бонус за реферальную программу"""
    active_referrals: list[Referrals] = await AsyncOrm.get_active_referrals(session)

    for ref in active_referrals:
        # проверяем появился ли подтвержденный платеж
        check_payments: bool = await AsyncOrm.is_confirmed_payment_exists_for_user(ref.to_user_id, session)

        # если подтвержденный платеж есть
        if check_payments:

            # начисляем бонус, переводи is_used в true, создаем payment о начислении за реф. ссылку
            await AsyncOrm.add_money_for_ref(ref.to_user_id, ref.from_user_id, settings.ref_bonus, session)

            # оповещаем пользователя
            msg = ms.get_money_for_ref_message(ref.to_user_id)
            await bot.send_message(ref.from_user_id, msg)


async def refresh_current_traffic(session: Any, bot: aiogram.Bot) -> None:
    """Скидывает трафик (устанавливает текущее значение в 0 Гб), каждые 30 дней"""

    print("Выполняется ежедневный шедулер")
    all_connections = await AsyncOrm.get_all_connections(session)

    for conn in all_connections:

        # проверяем сколько дней прошло с дня активации ключа
        if (datetime.datetime.now() - conn.start_date).days % settings.paid_period == 0:

            # получаем необходимый сервер
            server = await AsyncOrm.get_server(server_id=conn.server_id, session=session)

            # скидывает трафик
            await service.refresh_client_current_traffic(server=server, client_email=conn.email)

            # оповещаем пользователя об обновлении трафика
            message = ms.refresh_key_traffic(conn)
            await bot.send_message(conn.tg_id, message)



