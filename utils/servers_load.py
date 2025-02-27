from typing import Any

from database.orm import AsyncOrm


async def get_less_loaded_server(session: Any) -> int:
    """Возвращает id самого ненагруженного сервера"""
    servers_load: dict[int:int] = {}

    servers_ids_connections = await AsyncOrm.get_all_servers_id_from_connections(session)

    # при отсутствии созданных ранее подключений
    if not servers_ids_connections:
        return 1

    for server in servers_ids_connections:
        if server in servers_load:
            servers_load[server] += 1
        else:
            servers_load[server] = 1

    return min(servers_load, key=lambda x: servers_load[x])
