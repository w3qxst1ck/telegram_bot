import datetime

import pytz
from py3xui import AsyncApi, Inbound, Client

from settings import settings
from logger import logger


async def get_client(xui: AsyncApi, email: str) -> Client:
    """Получение клиента по email из панели 3x-ui"""
    await xui.login()

    try:
        response = await xui.client.get_by_email(email)
        return response

    except Exception as e:
        logger.error(f"Ошибка при получении из панели пользователя {email}: {e}")


async def create_client(xui: AsyncApi, inbound_id: int, client_uuid: str, tg_id: str, domain: str) -> str:
    """Создание клиента в панели 3x-ui"""
    await xui.login()

    try:
        await xui.client.add(
            inbound_id,
            [
                Client(
                    email=client_uuid,
                    enable=True,
                    tg_id=tg_id,
                    id=client_uuid,
                    flow=settings.server.flow,
                    total_gb=settings.traffic_limit * 1024**3,
                    limit_ip=1
                )
            ]
        )

        # генерация ключа для пользователя
        server = await xui.inbound.get_by_id(inbound_id)
        key = _generate_key(server, client_uuid, domain)
        return key

    except Exception as e:
        logger.error(f"Ошибка при создании ключа {client_uuid} пользователю {tg_id}: {e}")


async def block_key(xui: AsyncApi, email: str, tg_id: str) -> None:
    """Блокировка ключа (устанавливаем прошедшую дату)"""
    await xui.login()

    try:
        client: Client = await xui.client.get_by_email(email)
        # добавляем недостающие данные
        client.id = email
        client.tg_id = tg_id
        client.flow = settings.server.flow

        client.enable = False
        client.expiry_time = int((datetime.datetime.now(tz=pytz.timezone("Europe/Moscow")) - datetime.timedelta(
            days=1)).timestamp() * 1000)

        await xui.client.update(email, client)

    except Exception as e:
        logger.error(f"Ошибка при блокировке клиента {email} в панели: {e}")


async def activate_key(xui: AsyncApi, email: str, tg_id: str):
    """Разблокировка ключа (снятие ограничения по дате)"""
    await xui.login()

    try:
        client: Client = await xui.client.get_by_email(email)
        # добавляем недостающие данные
        client.id = email
        client.tg_id = tg_id
        client.flow = settings.server.flow

        client.enable = True
        client.expiry_time = 0

        await xui.client.update(email, client)

    except Exception as e:
        logger.error(f"Ошибка при активации клиента {email} в панели: {e}")


async def delete_key(xui: AsyncApi, email: str):
    """Удаление клиента из сервиса"""
    await xui.login()

    try:
        await xui.client.delete(1, email)

    except Exception as e:
        logger.error(f"Ошибка при удалении клиента {email} в панели: {e}")


async def get_current_traffic(xui: AsyncApi, email: str) -> float:
    """Получает потраченный клиентом трафик в Gb"""
    await xui.login()

    try:
        client: Client = await xui.client.get_by_email(email)
        traffic: float = _convert_traffic(client.up, client.down)
        return traffic

    except Exception as e:
        logger.error(f"Ошибка при получении трафика клиента {email}: {e}")


async def get_current_traffic_without_login(xui: AsyncApi, email: str) -> float:
    """Получает потраченный клиентом трафик в Gb"""
    try:
        client: Client = await xui.client.get_by_email(email)
        traffic = _convert_traffic(client.up, client.down)
        return traffic

    except Exception as e:
        logger.error(f"Ошибка при получении трафика клиента {email}: {e}")


async def refresh_key_traffic_by_email(xui: AsyncApi, inbound_id: int, email: str) -> None:
    """Обнуляет текущий трафик для ключа"""
    await xui.login()

    try:
        await xui.client.reset_stats(inbound_id=inbound_id, email=email)
        logger.info(f"Обновлен трафик ключа: {email}")

    except Exception as e:
        logger.error(f"Ошибка при обновлении (обнулении) текущего трафика для ключа {email}: {e}")


def _generate_key(server: Inbound, client_uuid: str, domain: str) -> str:
    """Создание строки подключения"""
    key = f"{server.protocol}://{client_uuid}@{domain}:{server.port}" \
          f"?type={server.stream_settings.network}" \
          f"&security={server.stream_settings.security}" \
          f"&pbk={server.stream_settings.reality_settings['settings']['publicKey']}" \
          f"&fp={server.stream_settings.reality_settings['settings']['fingerprint']}" \
          f"&sni={server.stream_settings.reality_settings['serverNames'][0]}" \
          f"&sid={server.stream_settings.reality_settings['shortIds'][0]}" \
          f"&spx={'%2F' if server.stream_settings.reality_settings['settings']['spiderX'] == '/' else ''}" \
          f"&flow={settings.server.flow}#{client_uuid}"
    return key


def _convert_traffic(up: int, down: int) -> float:
    """Переводит из байт в Гб"""
    summ = (up + down) / 1024 / 1024 / 1024
    return round(summ, 2)