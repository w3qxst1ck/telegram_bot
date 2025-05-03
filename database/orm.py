import datetime
from collections.abc import Mapping
from pydantic import ValidationError
from typing import Any, List

import asyncpg

from database.database import async_engine
from database.tables import Base

from schemas.user import UserAdd, UserConnList
from schemas.payments import Payments
from schemas.referrals import Referrals
from schemas.connection import Connection, ConnServerScheduler, Server, ServerAdd, ConnectionServer, ConnectionRegion
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
            created_at = datetime.datetime.now()
            await session.execute("""
                INSERT INTO users (tg_id, username, firstname, lastname, balance, trial_used, created_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                ON CONFLICT (tg_id) DO NOTHING
                """,
                                  user.tg_id,
                                  user.username,
                                  user.firstname,
                                  user.lastname,
                                  user.balance,
                                  user.trial_used,
                                  created_at
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
                    ORDER BY is_trial DESC, c.active DESC
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
            session: Any) -> id:
        """
            Покупка нового ключа и транзакционное уменьшение баланса
            Return: connection id: int
        """
        try:
            async with session.transaction():
                conn_id = await session.fetchval(
                    """
                    INSERT INTO connections (tg_id, active, start_date, expire_date, is_trial, email, key, description, server_id)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                    RETURNING id;
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

                return conn_id

        except Exception as e:
            logger.error(f"Ошибка создания connection и списания средств с баланся пользователя {c.tg_id}: {e}")
            raise

    @staticmethod
    async def extend_key(email: str,
                         start_date: datetime.datetime,
                         expire_date: datetime.datetime,
                         tg_id: str,
                         balance: int,
                         session: Any) -> None:
        """Продления ключа и транзакционное уменьшение баланса"""
        try:
            async with session.transaction():
                await session.execute(
                    """
                    UPDATE connections SET start_date = $1, expire_date = $2, active = true
                    WHERE email = $3;
                    """,
                    start_date, expire_date, email
                )
                await session.execute(
                    """
                    UPDATE users
                    SET balance = $1
                    WHERE tg_id = $2;
                    """,
                    balance, tg_id
                )

        except Exception as e:
            logger.error(f"Ошибка продления ключа {email} пользователя {tg_id}: {e}")
            raise

    @staticmethod
    async def get_connection_id(email: str, session) -> int:
        """Получение connection.id по email"""
        try:
            conn_id = await session.fetchval(
                """
                SELECT id FROM connections
                WHERE email = $1
                """,
                email
            )
            return conn_id
        except Exception as e:
            logger.error(f"Ошибка получения connection.id с email {email}: {e}")

    @staticmethod
    async def get_connection_by_id(conn_id: int, session) -> Connection:
        """Получение connection по email"""
        try:
            row = await session.fetchrow(
                """
                SELECT * FROM connections
                WHERE id = $1
                """,
                conn_id
            )
            conn = Connection.model_validate(row)
            return conn

        except ValidationError:
            raise

        except Exception as e:
            logger.error(f"Ошибка получения connection с id {conn_id}: {e}")

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
    async def get_all_servers_id_from_connections(session: Any, region: str = None) -> list[int]:
        """Получает list всех server_id из таблицы connections, если передан регион,
        то возвращает ключи этого региона"""
        try:
            if region:
                query = await session.fetch(
                    """
                    SELECT c.server_id from connections c
                    JOIN servers s ON c.server_id=s.id
                    WHERE s.region=$1 
                    """,
                    region
                )
            else:
                query = await session.fetch(
                    """
                    SELECT server_id from connections
                    """
                )

            return [row["server_id"] for row in query]

        except Exception as e:
            logger.error(f"Ошибка при получении id всех серверов из connections: {e}")

    @staticmethod
    async def get_server_countries(session: Any) -> List[str]:
        """Получает list уникальных regions из таблицы servers"""
        try:
            query = await session.fetch("""
                SELECT DISTINCT region from servers
                ORDER BY region
                """)

            return [row["region"] for row in query]

        except Exception as e:
            logger.error(f"Ошибка при получении уникальных region всех серверов: {e}")

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
    async def get_servers_ids(session: Any, region: str = None) -> list[int]:
        """Получение id всех серверов (при передаче региона, то вернутся сервера только этого региона)"""
        try:
            if region:
                query = await session.fetch(
                    """
                    SELECT id from servers
                    WHERE region=$1
                    """,
                    region
                )
            else:
                query = await session.fetch(
                    """
                    SELECT id from servers
                    """
                )
            return [server["id"] for server in query]

        except Exception as e:
            logger.error(f"Ошибка при получении id серверов: {e}")

    @staticmethod
    async def get_all_connections(session: Any) -> list[Connection]:
        """Получает все подключения """
        try:
            query = await session.fetch(
                """
                SELECT * FROM connections
                WHERE is_trial = false 
                """
            )
            connections: list[Connection] = [Connection.model_validate(conn) for conn in query]
            return connections

        except Exception as e:
            logger.error(f"Ошибка при получении всех connections: {e}")

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
            raise

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
    async def init_payment(tg_id: str, amount: int, created_at: datetime.datetime, description: str, session: Any) -> int:
        """Создание еще неподтвержденного платежа"""
        try:
            payment_id = await session.fetchval(
                """
                INSERT INTO payments (created_at, amount, status, description, user_tg_id)
                VALUES ($1, $2, $3, $4, $5)
                RETURNING id
                """,
                created_at, amount, False, description, tg_id
            )

            return payment_id
        except Exception as e:
            logger.error(f"Ошибка при создании платежа пользователя {tg_id} на сумму {amount}: {e}")
            raise

    @staticmethod
    async def confirm_payment(payment_id: int, tg_id: str, amount: int, session: Any) -> None:
        """Обновление статуса платежа и пополнение баланса"""
        try:
            async with session.transaction():
                await session.execute(
                    """
                    UPDATE payments
                    SET status=true
                    WHERE id = $1 AND user_tg_id = $2
                    """,
                    payment_id, tg_id
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

    @staticmethod
    async def get_active_user_connections(tg_id: str, session: Any) -> list[ConnectionRegion]:
        """Получает id и description активных connections пользователя по tg_id"""
        try:
            query = await session.fetch(
                """
                SELECT c.id, c.description, s.region 
                FROM connections AS c
                JOIN servers AS s ON c.server_id=s.id
                WHERE c.tg_id=$1 AND c.active=true AND c.is_trial=false
                """,
                tg_id
            )
            connections: list[ConnectionRegion] = [ConnectionRegion.model_validate(conn) for conn in query]
            return connections

        except Exception as e:
            logger.error(f"Ошибка при получении активных connections пользователя {tg_id}: {e}")

    @staticmethod
    async def get_user_balance(tg_id: str, session: Any) -> int:
        """Получение баланса у пользователя по tg_id"""
        try:
            query = await session.fetchval(
                """
                SELECT balance from users
                WHERE tg_id=$1
                """,
                tg_id
            )
            return query

        except Exception as e:
            logger.error(f"Ошибка при получении баланса пользователя {tg_id}: {e}")

    @staticmethod
    async def decrease_balance_on_amount(tg_id: str, amount: int, session: Any):
        """Уменьшить баланс на величину"""
        try:
            await session.execute(
                """
                UPDATE users
                SET balance = balance - $1
                WHERE tg_id = $2
                """,
                amount, tg_id
            )
        except Exception as e:
            logger.error(f"Ошибка при списании с баланса {amount} р. пользователя {tg_id}: {e}")
            raise

    @staticmethod
    async def get_user_payments(tg_id: str, session: Any) -> list[Payments]:
        """Получает список всех платежей пользователя (max - 10)"""
        try:
            rows = await session.fetch(
                """
                SELECT * FROM payments
                WHERE user_tg_id=$1
                ORDER BY created_at desc
                LIMIT 10
                """,
                tg_id
            )
            payments = [Payments.model_validate(row) for row in rows]
            return payments

        except Exception as e:
            logger.error(f"Ошибка при получении платежей пользователя {tg_id}: {e}")

    @staticmethod
    async def is_users_ref_relation_exists(tg_id: str, session: Any) -> bool:
        """Проверяем существует ли такая запись"""
        try:
            row_id = await session.fetchval(
                """
                SELECT id FROM referrals
                WHERE to_user_id=$1
                """,
                tg_id
            )

            return True if row_id else False

        except Exception as e:
            logger.error(f"Ошибка при получении cостояния реф. ссылки для {tg_id}: {e}")

    @staticmethod
    async def crete_users_ref_relation(tg_id: str, from_tg_id: str, session: Any) -> None:
        """Создает запись с приглашением от кого и для кого"""
        try:
            await session.execute(
                """
                INSERT INTO referrals(from_user_id, to_user_id, is_used)
                VALUES ($1, $2, false)
                """,
                from_tg_id, tg_id
            )

        except Exception as e:
            logger.error(f"Ошибка при создании записи о реф. ссылке от {tg_id} для {from_tg_id}: {e}")

    @staticmethod
    async def add_money_for_ref(tg_id: str, from_tg_id: str, amount: int, session: Any):
        """Начисляет деньги за реферальную программу и переводит ref.is_used в false"""
        try:
            async with session.transaction():
                await session.execute(
                    """
                    UPDATE referrals SET is_used=true 
                    WHERE to_user_id=$1
                    """,
                    tg_id)

                await session.execute(
                    """
                    UPDATE users
                    SET balance = balance + $1
                    WHERE tg_id = $2;
                    """,
                    amount, from_tg_id)

                await session.execute(
                    """
                    INSERT INTO payments (created_at, amount, status, description, user_tg_id)
                    VALUES ($1, $2, $3, $4, $5)
                    """,
                    datetime.datetime.now(), amount, True, f"REF_{tg_id}", from_tg_id
                )
                logger.info(f"Пользователю {from_tg_id} начислен бонус за использование реф. ссылки пользователем "
                            f"{tg_id}")

        except Exception as e:
            logger.error(f"Ошибка при начислен бонуса пользователю {from_tg_id} за использование реф. ссылки "
                         f"пользователем {tg_id}: {e}")

    @staticmethod
    async def get_active_referrals(session: Any) -> list[Referrals]:
        """Получает все реф. записи с is_used=false"""
        try:
            rows = await session.fetch(
                """
                SELECT * from referrals 
                WHERE is_used=false
                """
            )
            referrals = [Referrals.model_validate(row) for row in rows]
            return referrals

        except Exception as e:
            logger.error(f"Ошибка при получении всех незакрытых реф. записей: {e}")

    @staticmethod
    async def is_confirmed_payment_exists_for_user(tg_id: str, session: Any) -> bool:
        """Проверяем существует ли подтвержденный платеж пользователя"""
        try:
            query = await session.fetchval(
                """
                SELECT COUNT(*) FROM payments
                WHERE user_tg_id=$1 AND description IN ('STARS', 'ADD') AND status=true  
                """,
                tg_id
            )
            return query > 0

        except Exception as e:
            logger.error(f"Ошибка при получении количества подтвержденных платежей пользователя {tg_id}: {e}")

    @staticmethod
    async def create_payment(tg_id: str,
                             amount: int,
                             description: str,
                             status: bool,
                             created_at: datetime.datetime,
                             session: Any) -> None:
        """Создание платежа"""
        try:
            await session.execute(
                """
                INSERT INTO payments (created_at, amount, status, description, user_tg_id)
                VALUES ($1, $2, $3, $4, $5)
                """,
                created_at, amount, status, description, tg_id)

            logger.info(f"Создан платеж пользователя {tg_id} на сумму {amount} р.")

        except Exception as e:
            logger.error(f"Ошибка покупки создании платежа пользователя {tg_id}: {e}")

    @staticmethod
    async def up_balance(tg_id: str, summ: int, session: Any) -> None:
        """Пополнение баланса"""
        try:
            await session.execute(
                """
                UPDATE users
                SET balance = balance + $1
                WHERE tg_id=$2
                """,
                summ, tg_id
            )

        except Exception as e:
            logger.error(f"Ошибка при пополнении баланса пользователя {tg_id} на сумму {summ}: {e}")
            raise

    @staticmethod
    async def get_all_tg_ids(session: Any) -> List[str]:
        """Получение tg_id всех пользователей"""
        try:
            rows = await session.fetch(
                """
                SELECT tg_id 
                FROM users
                """
            )
            return [row["tg_id"] for row in rows]
        except Exception as e:
            logger.error(f"Ошибка при получении всех tg_id: {e}")

    @staticmethod
    async def get_expired_users_tg_ids(session: Any) -> List[str]:
        """Получение tg_id пользователей у которых неактивен ключ"""
        try:
            rows = await session.fetch(
                """
                SELECT DISTINCT tg_id
                FROM connections
                WHERE is_trial = false AND active = false
                """
            )
            return [row["tg_id"] for row in rows]
        except Exception as e:
            logger.error(f"Ошибка при получении всех tg_id, у которых неактивны ключи: {e}")

    @staticmethod
    async def get_active_users_tg_ids(session: Any) -> List[str]:
        """Получение tg_id пользователей у которых активен ключ"""
        try:
            rows = await session.fetch(
                """
                SELECT DISTINCT tg_id
                FROM connections
                WHERE is_trial = false AND active = true
                """
            )
            return [row["tg_id"] for row in rows]
        except Exception as e:
            logger.error(f"Ошибка при получении всех tg_id, у которых неактивны ключи: {e}")

    @staticmethod
    async def get_statistic_data(session: Any) -> dict:
        """Получение статистики по пользователям"""
        try:
            monthly_period = datetime.datetime.now() - datetime.timedelta(days=30)

            all_users = await session.fetchval(
                """
                SELECT COUNT(*) FROM users
                """
            )

            month_count_users = await session.fetchval(
                f"""
                SELECT COUNT(*) FROM users
                WHERE created_at > $1
                """,
                monthly_period
            )

            users_with_active_keys = await session.fetchval(
                """
                SELECT COUNT(*) FROM 
                    (
                    SELECT DISTINCT tg_id FROM connections AS c
                    WHERE c.active = true AND c.is_trial = false 
                    ) as temp
                """
            )

            all_keys = await session.fetchval(
                """
                SELECT COUNT(*) FROM connections
                """
            )

            trial_keys = await session.fetchval(
                """
                SELECT COUNT(*) FROM connections
                WHERE is_trial = true
                """
            )

            active_keys = await session.fetchval(
                """
                SELECT COUNT(*) FROM connections
                WHERE is_trial = false AND active = true
                """
            )

            payments_transfer_all_time = await session.fetchval(
                """
                SELECT SUM(p.amount) FROM payments AS p
                WHERE p.description = 'ADD' AND p.status = true
                """
            )

            payments_transfer_last_period = await session.fetchval(
                f"""
                SELECT SUM(p.amount) FROM payments AS p
                WHERE p.description = 'ADD' AND p.status = true AND p.created_at > $1
                """,
                monthly_period
            )

            payments_stars_all_time = await session.fetchval(
                """
                SELECT SUM(p.amount) FROM payments AS p
                WHERE p.description = 'STARS' AND p.status = true
                """
            )

            payments_stars_last_period = await session.fetchval(
                """
                SELECT SUM(p.amount) FROM payments AS p
                WHERE p.description = 'STARS' AND p.status = true AND p.created_at > $1
                """,
                monthly_period
            )

            referral_users = await session.fetchval(
                """
                SELECT COUNT(*)
                FROM referrals
                """
            )

            active_referral_users = await session.fetchval(
                """
                SELECT COUNT(*)
                FROM referrals
                WHERE is_used = true
                """
            )

            data = {
                "all_users": all_users,
                "month_count_users": month_count_users if month_count_users else 0,
                "users_with_active_keys": users_with_active_keys if users_with_active_keys else 0,
                "all_keys": all_keys if all_keys else 0,
                "trial_keys": trial_keys if trial_keys else 0,
                "active_keys": active_keys if active_keys else 0,
                "payments_transfer_all_time": payments_transfer_all_time if payments_transfer_all_time else 0,
                "payments_transfer_last_period": payments_transfer_last_period if payments_transfer_last_period else 0,
                "payments_stars_all_time": payments_stars_all_time if payments_stars_all_time else 0,
                "payments_stars_last_period": payments_stars_last_period if payments_stars_last_period else 0,
                "referral_users": referral_users if referral_users else 0,
                "active_referral_users": active_referral_users if active_referral_users else 0
            }
            return data

        except Exception as e:
            logger.error(f"Ошибка при получении статистики о пользователях: {e}")
