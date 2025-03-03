from typing import Any

from py3xui import AsyncApi

from settings import settings
from services.panel import create_client, block_key, delete_key, activate_key
from schemas.connection import Server
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
