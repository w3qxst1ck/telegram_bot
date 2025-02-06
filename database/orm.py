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
    async def create_user_test(session: Any, user: UserAdd):
        """Test method"""
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
            raise
