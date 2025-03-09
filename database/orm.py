import datetime
from collections.abc import Mapping
from typing import Any, List

import asyncpg

from database.database import async_engine
from database.tables import Base

from schemas.user import UserAdd, UserConnList
from schemas.connection import Connection, ConnServerScheduler, Server, ServerAdd, ConnectionServer
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
                    SELECT c.*, s.region, s.domain, s.api_url, s.inbound_id, s.name
                    FROM connections AS c
                    JOIN servers AS s ON c.server_id = s.id 
                    WHERE c.tg_id = $1
                    ORDER BY c.active DESC
                    """,
                    tg_id
                )
            else:
                conns_rows = await session.fetch(
                    """
                    SELECT c.*, s.region, s.domain, s.api_url, s.inbound_id, s.name
                    FROM connections AS c
                    JOIN servers AS s ON c.server_id = s.id
                    WHERE c.tg_id = $1 AND c.is_trial = false
                    ORDER BY c.active DESC
                    """,
                    tg_id)

            # если есть коннекты
            if conns_rows:
                conns: List[ConnectionServer] = [ConnectionServer.model_validate(row) for row in conns_rows]
                user_conns.connections = conns

            return user_conns

        except Exception as e:
            logger.error(f"Ошибка получения пользователя с коннектами и серверами {tg_id}: {e}")

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
                    INSERT INTO connections (tg_id, active, start_date, expire_date, is_trial, email, key, description, server_id)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9);
                    """,
                    c.tg_id, c.active, c.start_date, c.expire_date, c.is_trial, c.email, c.key, c.description, c.server_id)
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
            logger.error(f"Ошибка покупки ключа пользователя {c.tg_id}: {e}")
            raise

    @staticmethod
    async def extend_key(email: str, expire_date: datetime.datetime, tg_id: str, balance: int, session: Any) -> None:
        """Продления ключа и транзакционное уменьшение баланса"""
        try:
            async with session.transaction():
                await session.execute(
                    """
                    UPDATE connections SET expire_date = $1, active=true
                    WHERE email = $2;
                    """,
                    expire_date, email
                )
                await session.execute(
                    """
                    UPDATE users
                    SET balance = $1
                    WHERE tg_id = $2;
                    """,
                    balance, tg_id
                )
                logger.info(f"Пользователь {tg_id} продлил ключ {email} до {expire_date}")
        except Exception as e:
            logger.error(f"Ошибка продления ключа {email} пользователя {tg_id}: {e}")
            raise

    @staticmethod
    async def get_connection(email: str, session) -> Connection:
        """Получение connection по email"""
        try:
            row = await session.fetchrow(
                """
                SELECT * FROM connections
                WHERE email = $1
                """,
                email
            )
            conn = Connection.model_validate(row)
            return conn
        except Exception as e:
            logger.error(f"Ошибка получения connection с email {email}: {e}")

    @staticmethod
    async def get_connection_server(email: str, session) -> ConnectionServer:
        """Получение connection с server по email"""
        try:
            row = await session.fetchrow("""
                SELECT c.*, s.name, s.region, s.api_url, s.domain, s.inbound_id 
                FROM connections AS c
                JOIN servers AS s ON c.server_id = s.id
                WHERE c.email = $1
                """, email)
            conn = ConnectionServer.model_validate(row)
            return conn
        except Exception as e:
            logger.error(f"Ошибка получения connection с email {email}: {e}")

    @staticmethod
    async def get_all_servers(session: Any) -> list[Server]:
        """Получение всех серверов"""
        try:
            query = await session.fetch(
                """
                SELECT * FROM servers;
                """
            )
            servers_list = [Server.model_validate(row) for row in query]
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
            return [row["server_id"] for row in query]
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
            logger.error(f"Ошибка при получении id серверов: {e}")

    @staticmethod
    async def get_active_connections(session: Any) -> list[Connection]:
        """Получает все активные подключения"""
        try:
            query = await session.fetch(
                """
                SELECT * FROM connections
                WHERE active=true
                """
            )
            connections: list[Connection] = [Connection.model_validate(conn) for conn in query]
            return connections

        except Exception as e:
            logger.error(f"Ошибка при получении всех connections: {e}")

    @staticmethod
    async def deactivate_connection(email: str, session: Any):
        """Перевод active в False"""
        try:
            await session.execute(
                """
                UPDATE connections SET active=false
                WHERE email=$1
                """,
                email
            )
        except Exception as e:
            logger.error(f"Ошибка при переводе connection.action в false: {e}")

    @staticmethod
    async def delete_connection(email: str, session: Any):
        """Удаление connection"""
        try:
            await session.execute(
                """
                DELETE from connections 
                WHERE email=$1
                """,
                email
            )

        except Exception as e:
            logger.error(f"Ошибка при удалении connection {email}: {e}")

    @staticmethod
    async def set_trial_used_true(tg_id: str, session: Any):
        """Перевод trial_used в значение True"""
        try:
            await session.execute(
                """
                UPDATE users SET trial_used=true 
                WHERE tg_id=$1
                """,
                tg_id
            )

        except Exception as e:
            logger.error(f"Ошибка при обновлении статуса об использовании пробного периода у польз-ля {tg_id}: {e}")

    @staticmethod
    async def get_connections_with_servers(session: Any) -> list[ConnServerScheduler]:
        """Получение всех активных connections + поля из таблицы servers"""
        try:
            rows = await session.fetch(
                """
                SELECT tg_id, email, description, api_url, inbound_id
                FROM connections
                INNER JOIN servers on connections.server_id = servers.id
                WHERE active = true
                """
            )
            conn_servers = [ConnServerScheduler.model_validate(row) for row in rows]
            return conn_servers

        except Exception as e:
            logger.error(f"Ошибка при получении данных для ConnServerScheduler: {e}")

    @staticmethod
    async def init_payment(tg_id: str, amount: int, created_at:datetime.datetime, session: Any) -> None:
        """Создание еще неподтвержденного платежа"""
        try:
            await session.execute(
                """
                INSERT INTO payments (created_at, amount, status, user_tg_id)
                VALUES ($1, $2, $3, $4)
                """,
                created_at, amount, False, tg_id
            )
        except Exception as e:
            logger.error(f"Ошибка при создании платежа пользователя {tg_id} на сумму {amount}: {e}")
            raise

    @staticmethod
    async def confirm_payment(tg_id: str, amount: int, session: Any) -> None:
        """Обновление статуса платежа и пополнение баланса"""
        try:
            async with session.transaction():
                await session.execute(
                    """
                    UPDATE payments
                    SET status=true
                    WHERE user_tg_id = $1
                    """,
                    tg_id
                )
                await session.execute(
                    """
                    UPDATE users
                    SET balance = balance + $1
                    WHERE tg_id = $2
                    """,
                    amount, tg_id
                )
        except Exception as e:
            logger.error(f"Ошибка при подтверждении платежа пользователя {tg_id} на сумму {amount}: {e}")
            raise