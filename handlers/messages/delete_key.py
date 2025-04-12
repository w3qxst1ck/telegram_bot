import datetime

import pytz

from handlers.buttons.regions import FLAGS
from settings import settings
from schemas.user import UserConnList
from utils.date_time_service import convert_date_time
from handlers.buttons import menu as btn
from handlers.buttons import commands as cmd
from schemas.connection import ConnectionServer


def delete_key_menu(user_with_conns: UserConnList) -> str:
    """Сообщение при выборе какой ключ удалить"""
    if len(user_with_conns.connections) == 0:
        message = "У вас нет ключей, которые можно удалить"
    else:
        message = "Выберите ключ который хотите удалить"

    return message


def confirm_delete_key(conn_server: ConnectionServer) -> str:
    """Запрос подтверждения удаления ключа"""
    date, time = convert_date_time(conn_server.expire_date, with_tz=True)
    active_phrase = f"({'✅ активен до ' + time + ' ' + date if conn_server.active else '❌ неактивен'})"
    flag = FLAGS[conn_server.region]

    message = f"Вы уверены что хотите удалить ключ {flag} <b>{conn_server.description}</b> {active_phrase}?"
    return message


def key_deleted() -> str:
    """Сообщение об успешном удалении ключа"""
    message = "✅ Ключ успешно удален"
    return message

