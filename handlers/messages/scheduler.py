from handlers.buttons import commands as cmd
from schemas.connection import Connection


def expire_trial_key(trial_key: str) -> str:
    """Сообщение об окончании пробного ключа"""
    message = f"⛔️ Истек период использования пробного ключа\n```{trial_key}```\n\n*❗️ключ удален*\n\n" \
              f"Посмотреть свои ключи, профиль, пополнить баланс и купить ключ вы можете в /{cmd.MENU[0]}"

    return message


def expire_key(connection: Connection) -> str:
    """Сообщение об окончании срока ключа"""
    message = f"⛔️ Истек оплаченный период ключа *{connection.description}*\n```{connection.key}```\n\n" \
              f"ключ *{connection.description} заблокирован*\n\n" \
              f"Пополнить баланс и продлить ключ вы можете в разделе /{cmd.BUY[0]}"

    return message
