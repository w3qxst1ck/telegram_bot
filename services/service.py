import datetime

import pytz
from py3xui import AsyncApi, Inbound, Client

from settings import settings


class ClientService:

    def __init__(self, url: str, hostname: str, password: str, domain: str, flow: str):
        self.api = AsyncApi(url, hostname, password)
        self.url = url
        self.domain = domain
        self.flow = flow

    async def login(self):
        """Логин по username и password для vless panel"""
        await self.api.login()

    async def get_inbound(self) -> Inbound:
        """Получение подключения"""
        servers = await self.api.inbound.get_list()
        return servers[0]

    async def get_client(self, email: str) -> Client:
        """Получение клиента по email"""
        client = await self.api.client.get_by_email(email)
        return client

    async def get_clients(self) -> list:
        """Получение клиентов из inbound"""
        server = await self.get_inbound()
        clients = server.client_stats

        result = []
        for client in clients:
            result.append(client)

        return result

    async def add_client(self, client_uuid: str, tg_id: str) -> str:
        """Создание клиента и генерация ключа"""
        await self.api.client.add(
            1,
            [
                Client(
                    email=client_uuid,
                    enable=True,
                    tg_id=tg_id,
                    id=client_uuid,
                    flow=self.flow,
                )
            ]
        )
        key = await self._generate_key(client_uuid)
        return key

    async def block_client(self, email: str, tg_id: str):
        """Блокировка ключа (устанавливаем прошедшую дату)"""
        client: Client = await self.api.client.get_by_email(email)
        # добавляем недостающие данные
        client.id = email
        client.tg_id = tg_id
        client.flow = self.flow

        client.enable = False
        client.expiry_time = int((datetime.datetime.now(tz=pytz.timezone("Europe/Moscow")) - datetime.timedelta(
            days=1)).timestamp() * 1000)

        await self.api.client.update(email, client)

    async def activate_client(self, email: str, tg_id: str):
        """Разблокировка ключа (снятие ограничения по дате)"""
        client: Client = await self.api.client.get_by_email(email)
        # добавляем недостающие данные
        client.id = email
        client.tg_id = tg_id
        client.flow = self.flow

        client.enable = True
        client.expiry_time = 0

        await self.api.client.update(email, client)

    async def delete_client(self, email: str):
        """Удаление клиента из сервиса"""
        await self.api.client.delete(1, email)

    async def get_current_traffic(self, email: str) -> float:
        """Получает потраченный клиентом трафик в Gb"""
        client: Client = await self.get_client(email)
        traffic = await self.convert_traffic(client.up, client.down)
        return traffic

    async def _generate_key(self, client_uuid: str) -> str:
        """Создание строки подключения"""
        server = await self.get_inbound()

        key = f"{server.protocol}://{client_uuid}@{settings.servers['am-1']['domain']}:{server.port}" \
              f"?type={server.stream_settings.network}" \
              f"&security={server.stream_settings.security}" \
              f"&pbk={server.stream_settings.reality_settings['settings']['publicKey']}" \
              f"&fp={server.stream_settings.reality_settings['settings']['fingerprint']}" \
              f"&sni={server.stream_settings.reality_settings['serverNames'][0]}" \
              f"&sid={server.stream_settings.reality_settings['shortIds'][0]}" \
              f"&spx={'%2F' if server.stream_settings.reality_settings['settings']['spiderX'] == '/' else ''}" \
              f"&flow={settings.servers['am-1']['flow']}"
        return key

    @staticmethod
    async def convert_traffic(up: int, down: int) -> float:
        """Переводит из байт в Гб"""
        summ = (up + down) / 1024 / 1024 / 1024
        return round(summ, 2)


am_client = ClientService(
    url=settings.servers["am-1"]["url"],
    hostname=settings.servers["am-1"]["hostname"],
    password=settings.servers["am-1"]["password"],
    domain=settings.servers["am-1"]["domain"],
    flow=settings.servers["am-1"]["flow"],
)
