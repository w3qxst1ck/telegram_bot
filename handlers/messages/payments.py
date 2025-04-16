from typing import Any

from schemas.payments import Payments
from schemas.connection import Connection
from utils.date_time_service import convert_date_time
from logger import logger
from database.orm import AsyncOrm
from pydantic import ValidationError


async def user_payments_message(payments: list[Payments], balance: int, session: Any) -> str:
    """Сообщение со всеми операциями пользователя"""
    message = f"Баланс: <b>{balance} р.</b>\n\n"
    count = 0

    if not payments:
        return "У вас пока нет пополнений и списаний"

    for payment in payments:
        count += 1
        date, time = convert_date_time(payment.created_at, with_tz=True)
        pay_type = payment.description.split("_")[0]

        # пополнение баланса переводом
        if pay_type == "ADD":
            message += f"<b>{count}</b>. Пополнение <b>+{payment.amount} р. </b>{time} <b>{date}</b>\n{'✅ Платеж подтвержден' if payment.status else '❌ Не подтвержден'}\n\n"

        # пополнение баланса звездами
        elif pay_type == "STARS":
            message += f"<b>{count}</b>. Пополнение <b>+{payment.amount} р. </b>{time} <b>{date}</b>\n✅ Оплата телеграм звездами\n\n"

        # пополнения по реферальным ссылкам
        elif pay_type == "REF":
            message += f"<b>{count}</b>. Пополнение <b>+{payment.amount} р. </b>{time} <b>{date}</b>\n✅ Начисление за приглашение\n\n"

        # платежи за ключи
        elif pay_type == "KEY":
            try:
                connection: Connection = await AsyncOrm.get_connection_by_id(int(payment.description.split("_")[1]), session)
                message += f"{count}. Списание <b>-{payment.amount} р. </b>{time} <b>{date}</b>\n🔻 Оплата ключа \"{connection.description}\"\n\n"

            # при удаленном ключе
            except ValidationError:
                message += f"{count}. Списание <b>-{payment.amount} р. </b>{time} <b>{date}</b>\n🔻 Оплата ключа\n\n"

            # при неожиданной ошибке
            except Exception as e:
                count -= 1
                logger.error(f"Ошибка при парсинге платежа по ключу: {e}")

        elif pay_type == "TRAF":
            try:
                connection: Connection = await AsyncOrm.get_connection_by_id(int(payment.description.split("_")[1]), session)
                message += f"{count}. Списание <b>-{payment.amount} р. </b>{time} <b>{date}</b>\n🔻 Обнуление трафика ключа \"{connection.description}\"\n\n"

            # при удаленном ключе
            except ValidationError:
                message += f"{count}. Списание <b>-{payment.amount} р. </b>{time} <b>{date}</b>\n🔻 Обнуление трафика ключа\n\n"

            # при неожиданной ошибке
            except Exception as e:
                count -= 1
                logger.error(f"Ошибка при парсинге платежа по ключу: {e}")

    return message
