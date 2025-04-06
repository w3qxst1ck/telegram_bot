from settings import settings
from schemas.user import UserConnList


def buy_message(user_with_conn: UserConnList) -> str:
    """Сообщение для команды /buy"""
    message = f"У вас на балансе <b>{user_with_conn.balance} р.</b>\n\n" \
              f"Стоимость ключа VPN <b>(100 ГБ в месяц)</b>\n" \
              f"• 1 месяц <b>{settings.price_list['1']} р.</b>\n" \
              f"• 3 месяца <b>{settings.price_list['3']} р.</b>\n" \
              f"• 6 месяцев <b>{settings.price_list['6']} р.</b>\n" \
              f"• 12 месяцев <b>{settings.price_list['12']} р.</b>\n\n" \
              f"Вы можете купить или продлить (оплаченный период будет добавлен к текущему) имеющийся ключ, " \
              f"а также пополнить баланс с помощью соответствующих кнопок ниже"

    return message






