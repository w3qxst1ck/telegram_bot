from handlers.buttons.commands import HELP, BALANCE
from handlers.buttons.menu import NOTIFICATION
from settings import settings


def invoice_message(summ: str, tg_id: str) -> str:
    """Сообщение о переводе денег"""
    message = f"Для зачисления суммы на баланс необходимо перевести {summ} р\. по указанному номеру телефона \(нажмите, чтобы скопировать номер\)\n\n" \
              f"`{settings.bank_phone}`\n{settings.card_name} \(Т\-Банк\)\n\n"\
              f"❗*ВАЖНО*: \n" \
              f"В комментарии к оплате укажите число `{tg_id}` \(нажмите на число, чтобы скопировать\) для идентификации и подтверждения вашего платежа\n\n" \
              f"После завершения оплаты нажмите кнопку *\"Оплатил\(а\)\"*\."
    return message


def not_enough_balance_message(period: str, price: int, balance: int) -> str:
    """Сообщение при отказе в покупке подписки за счет баланса"""
    message = f"⚠️ Недостаточно средств для покупки/продления подписки на {period} мес.\n" \
              f"Необходимо {price} р., ваш остаток на балансе {balance} р.\n\n" \
              f"Вы можете пополнить баланс на необходимую сумму по кнопке ниже"

    return message


def not_enough_money(price: int, balance: int) -> str:
    """Сообщение о нехватке денег на балансе при покупке"""
    message = f"⚠️ Недостаточно средств для совершения покупки\n" \
              f"Необходимо {price} р., ваш остаток на балансе {balance} р.\n\n" \
              f"Вы можете пополнить баланс в разделе /{BALANCE[0]}"

    return message


def paid_request_for_user(summ: str) -> str:
    """Сообщение пользователю после нажатия кнопки 'Оплатил'"""
    message = f"{NOTIFICATION} <b>Автоматическое уведомление</b>\n\n" \
              f"Ваш платеж на сумму {summ} р. ожидает подтверждение администратором. " \
              f"После подтверждения вам будет отправлено уведомление о пополнении баланса.\n\n" \
              f"⏳ <b>Дождитесь подтверждения оплаты от администратора</b>"
    return message


def paid_request_for_admin(summ: str, tg_id: str) -> str:
    """Сообщение пользователю после нажатия кнопки 'Оплатил'"""
    message = f"<a href='tg://user?id={tg_id}'>Пользователь</a> " \
              f"оплатил пополнение баланса на сумму <b>{summ} р.</b> " \
              f"(в комментарии к оплате должно быть указанно число <b>{tg_id}</b>)" \
              f"\n\nПодтвердите или отклоните оплату"
    return message


def paid_confirmed_for_user(summ: str) -> str:
    """Сообщение об подтверждении оплаты администратором"""
    message = f"{NOTIFICATION} <b>Автоматическое уведомление</b>\n\n" \
              f"✅ Администратор подтвердил платеж\n" \
              f"Ваш баланс пополнен на <b>{summ} р.</b>"
    return message


def paid_decline_for_user(summ: str) -> str:
    """Сообщение об отклонении оплаты администратором"""
    message = f"{NOTIFICATION} <b>Автоматическое уведомление</b>\n\n" \
              f"❌ Администратор не подтвердил оплату пополнения баланса на {summ} р.\n" \
              f"Вы можете связаться с администрацией с помощью команды /{HELP[0]}"
    return message
