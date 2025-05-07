from handlers.buttons import commands as cmd
from handlers.buttons import menu as btn
from schemas.connection import Connection
from settings import settings


def expire_trial_key(trial_key: str) -> str:
    """Сообщение об окончании пробного ключа"""
    message = f"⛔️ Истек период использования пробного ключа\n```{trial_key}```\n\n*❗️Ключ удален*\n\n" \
              f"Вам необходимо пополнить баланс и купить новый ключ в разделе \"{btn.BUY}\" главного меню\n\n" \
              f"Посмотреть свои ключи, профиль, пополнить баланс и купить ключ вы можете в /{cmd.MENU[0]}"

    return message


def expire_key(connection: Connection) -> str:
    """Сообщение об окончании срока ключа"""
    message = f"⛔️ Истек оплаченный период ключа *{connection.description}*\n```{connection.key}```\n\n" \
              f"Ключ *{connection.description} заблокирован*\n\n" \
              f"Пополнить баланс и продлить ключ вы можете в разделе /{cmd.BUY[0]}"

    return message


def refresh_key_traffic(connection: Connection) -> str:
    """Сообщение об обновлении трафика"""
    message = f"{btn.NOTIFICATION} <i>Системное уведомление</i>\n\n" \
              f"Текущий трафик вашего ключа \"<b>{connection.description}</b>\" обновлен!"

    return message


def get_money_for_ref_message(tg_id: str) -> str:
    """Оповещение при получении денег за реф. ссылку"""
    message = f"{btn.NOTIFICATION} <i>Системное уведомление</i>\n\n" \
              f"На ваш баланс начислено <b>{settings.ref_bonus} р.</b> за приглашение " \
              f"<a href='tg://user?id={tg_id}'>пользователя</a>"

    return message
