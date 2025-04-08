import datetime

import pytz

from handlers.buttons.regions import FLAGS
from settings import settings
from schemas.user import UserConnList
from utils.date_time_service import convert_date_time
from handlers.buttons import menu as btn
from handlers.buttons import commands as cmd


def extend_key_menu_message(user_with_conns: UserConnList) -> str:
    """Сообщение в меню продления ключа"""
    if user_with_conns.connections:
        message = f"У вас на балансе <b>{user_with_conns.balance} р.</b>\n\n" \
                  f"Стоимость продления ключа VPN\n" \
                  f"• 1 месяц <b>{settings.price_list['1']} р.</b>\n" \
                  f"• 3 месяца <b>{settings.price_list['3']} р.</b>\n" \
                  f"• 6 месяцев <b>{settings.price_list['6']} р.</b>\n" \
                  f"• 12 месяцев <b>{settings.price_list['12']} р.</b>\n\n" \
                  f"Выберите ключ, который необходимо продлить, с помощью кнопок ниже (если ключ еще активен, " \
                  f"срок продления будет прибавлен к текущему)\n\n" \
                  f"✅ - Активные ключи\n" \
                  f"❌ - Неактивные ключи"
    else:
        message = f"У вас еще нет купленных ключей для подключения VPN. Вы можете купить новый ключ с помощью " \
                  f"команды /{cmd.BUY[0]} или в разделе \"{btn.BUY}\" главного меню"
    return message


def extend_key_period_message(balance: int, description: str, active: bool, expire_date: datetime.datetime, region: str) -> str:
    """Сообщение с периодом продления ключа"""
    date, time = convert_date_time(expire_date, with_tz=True)
    active_phrase = f"({'✅ активен до ' + time + ' ' + date if active else '❌ неактивен'})"
    flag = FLAGS[region]
    message = f"У вас на балансе <b>{balance} р.</b>\n\n" \
              f"Стоимость продления ключа {flag} <b>{description}</b> {active_phrase}\n" \
              f"• 1 месяц <b>{settings.price_list['1']} р.</b>\n" \
              f"• 3 месяца <b>{settings.price_list['3']} р.</b>\n" \
              f"• 6 месяцев <b>{settings.price_list['6']} р.</b>\n" \
              f"• 12 месяцев <b>{settings.price_list['12']} р.</b>\n\n" \
              f"Для продления ключа выберите необходимый срок действия с помощью кнопок ниже"
    return message


def extend_key_confirm_message(period: str, description: str, price: int, region: str) -> str:
    """Сообщение подтверждения продления ключа"""
    flag = FLAGS[region]
    message = f"Продлить ключ {flag} <b>{description}</b> на <b>{period} мес.</b>?\n\n" \
              f"У вас с баланса будет списано <b>{price} р.</b>"
    return message


def extend_key_message(period: str, price: int, expire_date: datetime.datetime, description: str, balance: int, region: str) -> str:
    """Сообщение при продлении ключа за счет баланса"""
    date, time = convert_date_time(expire_date, with_tz=True)
    flag = FLAGS[region]

    message = f"✅ Поздравляем, Вы продлили ключ {flag} <b>{description}</b> на <b>{period} мес.</b>!\n\n" \
              f"С баланса списано {price}р. (остаток {balance} р.)\n" \
              f"Дата истечения ключа <b>{time} {date} (МСК)</b>\n\n" \
              f"Вы всегда можете узнать актуальный статус и срок окончания подписки во вкладке \"{btn.KEYS}\" главного меню " \
              f"или с помощью команды /{cmd.KEYS[0]}"
    return message