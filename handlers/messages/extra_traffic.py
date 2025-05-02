from settings import settings
from schemas.connection import Connection
from handlers.buttons import regions


def buy_extra_traffic_message(is_empty: bool) -> str:
    """Сообщение с информацией о доп. трафике"""
    if is_empty:
        message = "У вас нет ключей, для которых можно обновить трафик"

    else:
        message = "Выберите ключ, для которого вы бы хотели обновить трафик " \
                  "(текущий трафик выбранного ключа будет обнулен)\n\n" \
                  f"Стоимость - <b>{settings.extra_traffic_price} руб.</b>"

    return message


def confirm_buy_extra_traffic(conn: Connection, server_region: str, user_balance: int) -> str:
    """Подтверждение списания денег за доп. трафик"""
    flag = regions.FLAGS[server_region]

    message = f"У вас на балансе <b>{user_balance} р.</b>\n\n"
    message += f"Обновление трафика ключа {flag} <b>{conn.description}</b>\n"
    message += f"С вашего баланса будет списано <b>{settings.extra_traffic_price} р.</b>\n\n"

    return message


def success_buy_extra_traffic(conn: Connection, server_region: str) -> str:
    flag = regions.FLAGS[server_region]

    message = f"✅ Трафик ключа {flag} <b>{conn.description}</b> успешно обновлен"
    return message


