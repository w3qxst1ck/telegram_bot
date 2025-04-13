from settings import settings


def buy_message(user_balance: int) -> str:
    """Сообщение для команды /buy"""
    message = f"У вас на балансе <b>{user_balance} р.</b>\n\n" \
              f"Стоимость ключа VPN (100 ГБ в месяц)\n" \
              f"• 1 месяц <b>{settings.price_list['1']} р.</b>\n" \
              f"• 3 месяца <b>{settings.price_list['3']} р.</b>\n" \
              f"• 6 месяцев <b>{settings.price_list['6']} р.</b>\n" \
              f"• 12 месяцев <b>{settings.price_list['12']} р.</b>\n\n" \
              f"Вы можете купить или продлить имеющийся ключ (оплаченный период будет добавлен к текущему) " \
              f"с помощью соответствующих кнопок ниже"

    return message






