import datetime
from collections.abc import Mapping
from typing import Any, List

import asyncpg

from database.database import async_engine
from database.tables import Base

from schemas.user import UserAdd, UserSubscription
from settings import settings
from logger import logger


# для model_validate регистрируем возвращаемый из asyncpg.fetchrow класс Record
Mapping.register(asyncpg.Record)


class AsyncOrm:

    @staticmethod
    async def create_tables():
        """Создание таблиц"""
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    @staticmethod
    async def drop_tables():
        """Удаление таблиц"""
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    @staticmethod
    async def create_user(user: UserAdd, session: Any):
        """Создание пользователя"""
        try:
            await session.execute("""
                INSERT INTO users (tg_id, username, firstname, lastname)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (tg_id) DO NOTHING
                """,
                user.tg_id,
                user.username,
                user.firstname,
                user.lastname
            )
        except Exception as e:
            logger.error(f"Ошибка при создании пользователя {user.tg_id} "
                         f"{'@' + user.username if user.username else ''}: {e}")

    @staticmethod
    async def create_subscription(tg_id: str,
                                  active: bool,
                                  start_date: datetime.datetime | None,
                                  expire_date: datetime.datetime | None,
                                  is_trial: bool,
                                  trial_used: bool,
                                  session: Any):
        """Создание подписки для пользователя"""
        try:
            await session.execute("""
                INSERT INTO subscriptions (tg_id, active, start_date, expire_date, is_trial, trial_used)
                VALUES ($1, $2, $3, $4, $5, $6)
                ON CONFLICT (tg_id) DO NOTHING
                """,
                tg_id,
                active,
                start_date,
                expire_date,
                is_trial,
                trial_used
            )
        except Exception as e:
            logger.error(f"Ошибка при создании подписки {tg_id}: {e}")

    @staticmethod
    async def check_user_already_exists(tg_id: str, session: Any) -> bool:
        """Проверяет создан ли профиль пользователя в БД"""
        try:
            exists = await session.fetchval(
                """
                SELECT EXISTS(SELECT 1 FROM users WHERE tg_id = $1)
                """,
                tg_id
            )
            return exists
        except Exception as e:
            logger.error(f"Ошибка при проверке регистрации пользователя {tg_id}: {e}")

    @staticmethod
    async def get_trial_subscription_status(tg_id: str, session: Any) -> asyncpg.Record:
        """Получение статуса использования пробной подписки"""
        try:
            trial_status_row = await session.fetchrow(
                """
                SELECT active, is_trial, trial_used FROM subscriptions 
                WHERE tg_id = $1
                """,
                tg_id
            )

            return trial_status_row

        except Exception as e:
            logger.error(f"Ошибка при получении статуса пробной подписки {tg_id}: {e}")

    @staticmethod
    async def get_user_with_subscription(tg_id: str, session: Any) -> UserSubscription:
        """Получение user с подпиской"""
        try:
            row = await session.fetchrow(
                """
                SELECT * FROM users u
                JOIN subscriptions s ON u.tg_id = s.tg_id
                WHERE u.tg_id = $1
                """,
                tg_id
            )
            user_with_sub = UserSubscription.model_validate(row)
            return user_with_sub
        except Exception as e:
            logger.error(f"Ошибка получения пользователя с подпиской {tg_id}: {e}")

    @staticmethod
    async def activate_trial_subscription(tg_id: str, session: Any) -> None:
        """Активация пробной подписки"""
        start_date = datetime.datetime.now()
        expire_date = start_date + datetime.timedelta(days=settings.trial_days)

        try:
            await session.execute(
                """
                UPDATE subscriptions
                SET active = true, start_date = $1, expire_date = $2, is_trial = true
                WHERE tg_id = $3 
                """,
                start_date, expire_date, tg_id
            )
        except Exception as e:
            logger.error(f"Ошибка активации пробной подписки пользователя {tg_id}: {e}")

        pass

    @staticmethod
    async def create_key(tg_id: str, ui_key: str, description: str, session: Any) -> str:
        """Создание ключа
            return: key str
        """
        try:
            key = await session.fetchval(
                """
                INSERT INTO keys (tg_id, key, description) 
                VALUES($1, $2, $3)
                RETURNING key 
                """,
                tg_id, ui_key, description

            )
            return key

        except Exception as e:
            logger.error(f"Ошибка при создании ключа: {ui_key} пользователю: {tg_id} - {e}")
