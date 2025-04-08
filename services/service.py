from typing import Any, List

from py3xui import AsyncApi

from database.orm import AsyncOrm
from settings import settings
from services.panel import create_client, block_key, delete_key, activate_key, get_current_traffic, \
    get_current_traffic_without_login, refresh_key_traffic_by_email
from schemas.connection import Server, Connection
from logger import logger


async def add_client(server: Server, client_email: str, tg_id: str) -> str:
    """Создает ключ клиента в панели 3x-ui и возвращает его"""

    xui = AsyncApi(
        host=server.api_url,
        username=settings.server.username,
        password=settings.server.password
    )
    key = await create_client(
        xui,
        inbound_id=server.inbound_id,
        client_uuid=client_email,
        tg_id=tg_id,
        domain=server.domain
    )
    logger.info(f"Создан ключ {key} пользователя tg_id {tg_id} email {client_email}")
    return key


async def delete_client(server: Server, client_email: str) -> None:
    """Удаляет ключ в панели 3x-ui"""
    xui = AsyncApi(
        host=server.api_url,
        username=settings.server.username,
        password=settings.server.password
    )
    await delete_key(xui, client_email)
    logger.info(f"Удален ключ email {client_email}")


async def block_client(server: Server, client_email: str, tg_id: str) -> None:
    """Блокировка ключа в панели 3x-ui"""
    xui = AsyncApi(
        host=server.api_url,
        username=settings.server.username,
        password=settings.server.password
    )
    await block_key(xui, client_email, tg_id)
    logger.info(f"Заблокирован {client_email} ключ пользователя {tg_id}")


async def activate_client(server: Server, client_email: str, tg_id: str) -> None:
    """Активация клиента (ключа)"""
    xui = AsyncApi(
        host=server.api_url,
        username=settings.server.username,
        password=settings.server.password
    )
    await activate_key(xui, client_email, tg_id)
    logger.info(f"Активирован ключ {client_email} пользователя {tg_id}")


async def get_client_traffic(server_url: str, email: str) -> float:
    """Получение трафика клиента"""
    xui = AsyncApi(
        host=server_url,
        username=settings.server.username,
        password=settings.server.password
    )
    traffic = await get_current_traffic(xui, email)
    return traffic


async def get_client_traffic_for_all_keys(connections: List[Connection], session: Any) -> List[Connection]:
    """Получение трафика для всех ключей клиента"""
    credentials = {
        "server_id": 0,
        "current_xui": None
    }
    conns_with_traffic = []

    for conn in connections:
        if conn.server_id != credentials["server_id"]:
            server = await AsyncOrm.get_server(conn.server_id, session)
            xui = AsyncApi(
                host=server.api_url,
                username=settings.server.username,
                password=settings.server.password
            )
            await xui.login()
            credentials["current_xui"] = xui
            credentials["server_id"] = conn.server_id

        traffic = await get_current_traffic_without_login(credentials["current_xui"], conn.email)
        conn.traffic = traffic
        conns_with_traffic.append(conn)

    return conns_with_traffic


async def refresh_client_current_traffic(server: Server, client_email: str) -> None:
    """Обнуление трафика для ключа"""
    xui = AsyncApi(
        host=server.api_url,
        username=settings.server.username,
        password=settings.server.password
    )

    await refresh_key_traffic_by_email(xui, server.inbound_id, client_email)

