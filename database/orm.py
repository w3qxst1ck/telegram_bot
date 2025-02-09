from typing import Any

from database.database import async_engine
from database.tables import Base

from schemas.user import UserAdd
from logger import logger


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
    async def create_subscription(tg_id: str, session: Any):
        """Создание подписки для пользователя"""
        try:
            await session.execute("""
                INSERT INTO subscriptions (tg_id, active)
                VALUES ($1, $2)
                ON CONFLICT (tg_id) DO NOTHING
                """,
                tg_id,
                False
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
    async def create_test_subscription(tg_id: str, active: bool, is_used: bool, session: Any) -> None:
        """Создание тестовой (разовой) подписки пользователю"""
        try:
            await session.execute("""
                INSERT INTO trial_subscriptions (tg_id, active, is_used) 
                VALUES ($1, $2, $3)
                ON CONFLICT (tg_id) DO NOTHING
                """,
                tg_id,
                active,
                is_used
            )
        except Exception as e:
            logger.error(f"Ошибка при создании пробной подписки пользователю {tg_id}: {e}")

    @staticmethod
    async def get_trial_subscription_status(tg_id: str, session: Any) -> bool:
        """Получение статуса использования пробной подписки"""
        try:
            trial_status = await session.fetchval(
                """
                SELECT is_used FROM trial_subscriptions 
                WHERE tg_id = $1
                """,
                tg_id
            )
            return trial_status

        except Exception as e:
            logger.error(f"Ошибка при получении статуса пробной подписки {tg_id}: {e}")