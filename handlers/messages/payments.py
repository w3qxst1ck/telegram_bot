from typing import Any
import pytz

from schemas.payments import Payments
from schemas.connection import Connection
from utils.date_time_service import convert_date_time
from logger import logger
from database.orm import AsyncOrm
from settings import settings


async def user_payments_message(payments: list[Payments], balance: int, session: Any) -> str:
    """Сообщение со всеми операциями пользователя"""
    message = f"Баланс: <b>{balance} р.</b>\n\n"
    count = 0

    if not payments:
        return "У вас пока нет пополнений и списаний"

    for payment in payments:
        count += 1
        date, time = convert_date_time(payment.created_at, with_tz=True)

        # пополнение баланса
        if payment.description == "ADD":
            message += f"<b>{count}</b>. Пополнение <b>+{payment.amount} р.</b> {'✅' if payment.status else '❌ Не подтвержден'} {date} {time}\n\n"

        # пополнения по реферальным ссылкам
        elif payment.description == "REF":
            message += f"{count}. Поступление за приглашение <b>+{payment.amount} р.</b> ✅ {date} {time}\n\n"

        # платежи за ключи
        else:
            # TODO выбрать смайлик
            try:
                connection: Connection = await AsyncOrm.get_connection_by_id(int(payment.description), session)
                message += f"{count}. Списание <b>-{payment.amount} р.</b> оплата ключа \"{connection.description}\" {date} {time}\n\n"

            except Exception as e:
                logger.error(f"Ошибка при парсинге платежа по ключу: {e}")

    return message