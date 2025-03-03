from handlers.buttons import commands as cmd


def expire_trial_key(trial_key: str) -> str:
    """Сообщение об окончании пробного ключа"""
    message = f"⛔️ Истек пробный период ключа\n```{trial_key}```\n\n*ключ удален*\n\n" \
              f"Посмотреть свои ключи, профиль, пополнить баланс и купить ключ вы можете в /{cmd.MENU[0]}"

    return message


def expire_key(key: str) -> str:
    """Сообщение об окончании срока ключа"""
    message = f"⛔️ Истек оплаченный период ключа\n```{key}```\n\n*ключ заблокирован*\n\n" \
              f"Пополнить баланс и продлить ключ вы можете в разделе /{cmd.BUY[0]}"

    return message
