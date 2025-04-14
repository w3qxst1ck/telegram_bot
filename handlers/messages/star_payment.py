from handlers.buttons.menu import NOTIFICATION


def up_balance_message(summ: int) -> str:
    """Сообщение об успешном пополнении баланса"""
    message = f"{NOTIFICATION} <b>Автоматическое уведомление</b>\n\n" \
              f"✅ Ваш баланс пополнен на <b>{summ} р.</b>"

    return message