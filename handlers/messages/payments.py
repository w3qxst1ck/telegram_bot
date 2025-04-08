
from schemas.payments import Payments
from utils.date_time_service import convert_date_time


def user_payments_message(payments: list[Payments], balance: int) -> str:
    """Сообщение со всеми операциями пользователя"""
    message = f"Баланс: <b>{balance} р.</b>\n\n"
    count = 0

    for payment in payments:
        count += 1
        date = convert_date_time(payment.created_at)

        # пополнение баланса
        if payment.description == "ADD":
            message += f"{count}. Пополнение +{payment.amount} р. {'✅' if payment.status else '❌'} {date}\n"

        # пополнения по реф. ссылкам
        elif payment.description == "REF":
            message += f"{count}. Поступление за приглашение +{payment.amount} р. ✅ {date}\n"

        # платежи за ключи
        else:
            # TODO выбрать смайлик
            message += f"{count}. Списание -{payment.amount} р. {date}\n"

    return message