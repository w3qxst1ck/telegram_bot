from settings import settings
from schemas.user import UserSubscription
from utils.date_time_service import convert_date_time


async def buy_message(user_with_sub: UserSubscription) -> str:
    """Сообщение для команды /buy"""
    date, time = convert_date_time(user_with_sub.expire_date)

    # если активна пробная или основная подписка
    if user_with_sub.active:

        # если активна пробная подписка
        if user_with_sub.is_trial:
            message = f"✅ У вас активирована <b>пробная подписка</b> на 1 день, она истекает {date} в {time}\n\n"

        # если активна основная подписка
        else:
            message = f"✅ Ваша подписка активна до <b>{date} {time}</b>\n\n"

    # если подписка неактивна
    else:
        message = f"❌ Ваша подписка <b>неактивна</b>\n\n"

    message += f"Стоимость подписки VPN на месяц <b>{settings.price}р</b>\n" \
               f"У вас на балансе ..... \n\n" \
               f"Вы можете купить или продлить (оплаченный период будет добавлен к текущему) подписку, " \
               f"а также пополнить баланс с помощью соответствующих кнопок ниже"

    return message