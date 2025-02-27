from typing import Any

from py3xui import AsyncApi

from settings import settings
from services.panel import create_client
from schemas.connection import Server


async def add_client(server: Server, client_email: str, tg_id: str) -> str:
    """
    Создает ключ клиента и возвращает его
    """

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
    return key


