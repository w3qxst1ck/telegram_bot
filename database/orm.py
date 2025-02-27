import datetime
from collections.abc import Mapping
from typing import Any, List

import asyncpg

from database.database import async_engine
from database.tables import Base

from schemas.user import UserAdd, UserConnList
from schemas.connection import Connection, Server, ServerAdd
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
    async def create_user(user: UserAdd, session: Any) -> None:
        """Создание пользователя"""
        try:
            await session.execute("""
                INSERT INTO users (tg_id, username, firstname, lastname, balance, trial_used)
                VALUES ($1, $2, $3, $4, $5, $6)
                ON CONFLICT (tg_id) DO NOTHING
                """,
                                  user.tg_id,
                                  user.username,
                                  user.firstname,
                                  user.lastname,
                                  user.balance,
                                  user.trial_used,
                                  )
        except Exception as e:
            logger.error(f"Ошибка при создании пользователя {user.tg_id} "
                         f"{'@' + user.username if user.username else ''}: {e}")

    @staticmethod
    async def get_user_id(tg_id: str, session: Any) -> int:
        """Получает id пользователя по tg_id"""
        try:
            user_id = await session.fetchval(
                """
                SELECT id FROM users WHERE tg_id=$1
                """,
                tg_id
            )
            return user_id
        except Exception as e:
            logger.error(f"Не удалось получить id пользователя {tg_id}: {e}")

    @staticmethod
    async def create_connection(tg_id: str,
                                active: bool,
                                start_date: datetime.datetime,
                                expire_date: datetime.datetime,
                                is_trial: bool,
                                email: str,
                                key: str,
                                description: str | None,
                                server_id: int,
                                session: Any):
        """Создание подключения для пользователя"""
        try:
            await session.execute(
                """
                INSERT INTO connections (tg_id, active, start_date, expire_date, 
                is_trial, email, key, description, server_id)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                """,
                tg_id, active, start_date, expire_date, is_trial, email, key, description, server_id
            )
            logger.info(f"Создан коннект с ключом {key} для пользователя {tg_id}")
        except Exception as e:
            logger.error(f"Ошибка при создании подключения {tg_id}: {e}")

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
    async def get_trial_connection_status(tg_id: str, session: Any) -> bool:
        """Получение статуса использования пробного ключа"""
        try:
            trial_used: bool = await session.fetchval(
                """
                SELECT trial_used FROM users 
                WHERE tg_id = $1
                """,
                tg_id
            )
            return trial_used

        except Exception as e:
            logger.error(f"Ошибка при получении статуса использования пробного ключа {tg_id}: {e}")

    @staticmethod
    async def get_user_with_connection_list(tg_id: str, session: Any, need_trial: bool = True) -> UserConnList:
        """Получение списка user с connection"""
        try:
            user_row = await session.fetchrow(
                """
                SELECT * FROM users
                WHERE tg_id = $1
                """,
                tg_id
            )

            user_conns = UserConnList(
                id=user_row["id"],
                created_at=user_row["created_at"],
                tg_id=user_row["tg_id"],
                username=user_row["username"],
                firstname=user_row["firstname"],
                lastname=user_row["lastname"],
                balance=user_row["balance"],
                trial_used=user_row["trial_used"],
                connections=[]
            )

            # с пробным ключом
            if need_trial:
                conns_rows = await session.fetch(
                    """
                    SELECT * 
                    FROM connections  
                    WHERE tg_id = $1
                    ORDER BY active DESC
                    """,
                    tg_id
                )
            else:
                conns_rows = await session.fetch(
                    """
                    SELECT * 
                    FROM connections  
                    WHERE tg_id = $1 AND is_trial = False
                    ORDER BY active DESC
                    """,
                    tg_id)

            # если есть коннекты
            if conns_rows:
                conns: List[Connection] = [Connection.model_validate(row) for row in conns_rows]
                user_conns.connections = conns

            return user_conns

        except Exception as e:
            logger.error(f"Ошибка получения пользователя с коннектами {tg_id}: {e}")
    #
    # @staticmethod
    # async def activate_trial_subscription(tg_id: str, session: Any) -> None:
    #     """Активация пробной подписки"""
    #     start_date = datetime.datetime.now()
    #     expire_date = start_date + datetime.timedelta(days=settings.trial_days)
    #
    #     try:
    #         await session.execute(
    #             """
    #             UPDATE subscriptions
    #             SET active = true, start_date = $1, expire_date = $2, is_trial = true
    #             WHERE tg_id = $3
    #             """,
    #             start_date, expire_date, tg_id
    #         )
    #     except Exception as e:
    #         logger.error(f"Ошибка активации пробной подписки пользователя {tg_id}: {e}")
    #
    #     pass

    @staticmethod
    async def buy_new_key(
            c: Connection,
            balance: int,
            session: Any) -> None:
        """Покупка нового ключа и транзакционное уменьшение баланса"""
        try:
            async with session.transaction():
                await session.execute(
                    """
                    INSERT INTO connections (tg_id, active, start_date, expire_date, is_trial, email, key, description)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9);
                    """,
                    c.tg_id, c.active, c.start_date, c.expire_date, c.is_trial, c.email, c.key, c.description)
                await session.execute(
                    """
                    UPDATE users
                    SET balance = $1 
                    WHERE tg_id = $2;
                    """,
                    balance, c.tg_id
                )
                logger.info(f"Пользователь {c.tg_id} купил новый ключ сроком до {c.expire_date}")
        except Exception as e:
            logger.error(f"Ошибка покупки/продления подписки пользователя {c.tg_id}: {e}")

    @staticmethod
    async def get_all_servers(session: Any) -> list[Server]:
        """Получение всех серверов"""
        try:
            query = await session.fetch(
                """
                SELECT * FROM servers;
                """
            )
            servers_list = [
                Server(
                    id=query["id"],
                    name=query["name"],
                    region=query["region"],
                    api_url=query["api_url"],
                    domain=query["domain"],
                    inbound_id=query["inbound_id"]
                )
            ]
            return servers_list

        except Exception as e:
            logger.error(f"Ошибка при получение всех серверов: {e}")

    @staticmethod
    async def get_server(server_id: int, session: Any) -> Server:
        """Получает сервер по id"""
        try:
            query = await session.fetchrow(
                """
                SELECT * from servers
                WHERE id=$1
                """,
                server_id
            )
            server = Server(
                id=query["id"],
                name=query["name"],
                region=query["region"],
                api_url=query["api_url"],
                domain=query["domain"],
                inbound_id=query["inbound_id"]

            )
            return server
        except Exception as e:
            logger.error(f"Ошибка при получение сервера {server_id}: {e}")

    @staticmethod
    async def get_all_servers_id_from_connections(session: Any) -> list[int]:
        """Получает list всех server_id из таблицы connections"""
        try:
            query = await session.fetch(
                """
                SELECT server_id from connections
                """
            )
            return query
        except Exception as e:
            logger.error(f"Ошибка при получении id всех серверов из connections: {e}")

    @staticmethod
    async def create_server(server: ServerAdd, session: Any) -> None:
        """Создание сервера"""
        try:
            await session.execute(
                """
                INSERT INTO servers (name, region, api_url, domain, inbound_id) 
                VALUES($1, $2, $3, $4, $5)
                """,
                server.name, server.region, server.api_url, server.domain, server.inbound_id
            )

        except Exception as e:
            logger.error(f"Ошибка при создании сервера {Server}: {e}")

    @staticmethod
    async def get_servers_ids(session: Any) -> list[int]:
        """Получение id всех серверов"""
        try:
            query = await session.fetch(
                """
                SELECT id from servers
                """
            )
            return [server["id"] for server in query]

        except Exception as e:
            logger.error(f"Оибка при получении id серверов: {e}")
