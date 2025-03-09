import datetime

import pytz

from settings import settings
from utils.date_time_service import convert_date_time
from handlers.buttons import menu as btn
from handlers.buttons import commands as cmd


def new_key_message(balance: int) -> str:
    """Сообщение для покупки нового ключа"""
    message = f"У вас на балансе <b>{balance}р</b>\n\n" \
               f"Стоимость ключа VPN\n" \
               f"• 1 месяц <b>{settings.price_list['1']}р</b>\n" \
               f"• 3 месяца <b>{settings.price_list['3']}р</b>\n" \
               f"• 6 месяцев <b>{settings.price_list['6']}р</b>\n" \
               f"• 12 месяцев <b>{settings.price_list['12']}р</b>\n\n" \
               f"Для покупки ключа выберите необходимый срок действия с помощью кнопок ниже"
    return message


def new_key_confirm_message(period: str, price: int) -> str:
    """Сообщение подтверждения покупки нового ключа"""
    message = f"Купить новый ключ на <b>{period} мес.</b>?\n\n" \
              f"У вас с баланса будет списано <b>{price}р.</b>"
    return message


def buy_new_key_message(period: str, price: int, expire_date: datetime.datetime, balance: int, key: str) -> str:
    """Сообщение при покупке нового ключа за счет баланса"""
    date, time = convert_date_time(expire_date.astimezone(tz=pytz.timezone(settings.timezone)))

    message = f"✅ Поздравляем, Вы купили ключ на *{period} мес.*!\n" \
              f"С баланса списано {price}р. (остаток {balance}р.)\n"\
              f"Дата истечения ключа *{time} {date} (МСК)*\n\n" \
              f"Нажмите на ключ, чтобы его скопировать\n" \
              f"```{key}```\n\n" \
              f"Вы всегда можете узнать актуальный статус и срок окончания подписки во вкладке \"{btn.KEYS}\" главного меню " \
              f"или с помощью команды /{cmd.KEYS[0]}"
    return message