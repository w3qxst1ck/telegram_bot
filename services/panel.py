from py3xui import AsyncApi

from settings import settings
from services.service import create_client


async def add_client(client_email: str, tg_id: str) -> str:
    """
    Создает клиента в панели 3x-ui, возвращает ключ для подключения
    """
    # TODO получить самый ненагруженный сервер через БД?
    # server: Server(url, name, url ...)

    xui = AsyncApi(
        host="https://somedomain123.store:2053/jA7PFJItw5/",    # TODO заменить на url из БД
        username=settings.server.hostname,
        password=settings.server.password
    )
    key = await create_client(xui, 1, client_email, tg_id) # TODO inbound_id брать из БД

    return key

