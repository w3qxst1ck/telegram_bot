from typing import Any

from database.orm import AsyncOrm


async def get_less_loaded_server(session: Any, region: str = None) -> int:
    """Возвращает id самого ненагруженного сервера"""
    servers_load: dict[int:int] = {}

    servers_ids_connections: list[int] = await AsyncOrm.get_all_servers_id_from_connections(session, region)
    all_servers_id: list[int] = await AsyncOrm.get_servers_ids(session, region)

    # при отсутствии созданных ранее подключений в выбранном регионе
    if not servers_ids_connections:
        return all_servers_id[0]

    # вносим все id серверов в hashmap
    for server_id in all_servers_id:
        servers_load[server_id] = 0

    # подсчитываем количество ключей на сервере
    for conn_server_id in servers_ids_connections:
        servers_load[conn_server_id] += 1

    return min(servers_load, key=lambda x: servers_load[x])
