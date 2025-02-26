import datetime

from settings import settings
from schemas.user import UserConnList
from utils.date_time_service import convert_date_time
from handlers.buttons import menu as btn
from handlers.buttons import commands as cmd


def buy_message(user_with_conn: UserConnList) -> str:
    """Сообщение для команды /buy"""
    message = ""

    # if user_with_conn.connections:
    #     for idx, conn in enumerate(user_with_conn.connections, start=1):
    #         date, time = convert_date_time(user_with_conn.expire_date)
    #
    #         # если активна пробная или основная подписка
    #         if conn.active:
    #
    #             # если активна пробная подписка
    #             if conn.is_trial:
    #                 message += f"<b>{idx}.</b> ✅ <b>Пробная подписка</b> на 1 день, она истекает <b>{date} в {time}</b> " \
    #                            f"(ключ {conn.email})\n\n"
    #
    #             # если активна основная подписка
    #             else:
    #                 message += f"<b>{idx}.</b> ✅ Ключ {conn.email} активен до <b>{date} {time}</b>\n" \
    #                            f"Какая-то инфа по ключу\n"
    #
    #         # если подписка неактивна
    #         else:
    #             message += f"<b>{idx}.</b> ❌ Ключ {conn.email} <b>неактивен</b>\n\n"
    # else:
    #     message += f"У вас еще нет приобретенных ключей для подключения VPN\n\n"

    message += f"У вас на балансе <b>{user_with_conn.balance}р</b>\n\n" \
               f"Стоимость ключа VPN\n" \
               f"• 1 месяц <b>{settings.price_list['1']}р</b>\n" \
               f"• 3 месяца <b>{settings.price_list['3']}р</b>\n" \
               f"• 6 месяцев <b>{settings.price_list['6']}р</b>\n" \
               f"• 12 месяцев <b>{settings.price_list['12']}р</b>\n\n" \
               f"Вы можете купить или продлить (оплаченный период будет добавлен к текущему) имеющийся ключ, " \
               f"а также пополнить баланс с помощью соответствующих кнопок ниже"

    return message


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


def new_key_confirm_message(period: str) -> str:
    """Сообщение подтверждения покупки нового ключа"""
    message = f"Купить новый ключ на <b>{period} мес.</b>?\n\n" \
              f"У вас с баланса будет списано <b>{settings.price_list[period]}р.</b>"
    return message


def invoice_message(summ: str, tg_id: str) -> str:
    """Сообщение о переводе денег"""
    message = ""
    message += f"Для зачисления суммы на баланс необходимо перевести {summ} руб\. по указанным реквизитам \(нажмите, чтобы скопировать реквизиты\)\n\n" \
               f"`0000 0000 0000 0000`\nАлександр \(Т\-Банк\)\n\n"
    message += f"❗*ВАЖНО*: \n" \
               f"В комментарии к оплате укажите число *{tg_id}* для идентификации и подтверждения вашего платежа\.\n\n" \
               f"После завершения оплаты нажмите кнопку *\"Оплатил\(а\)\"*\."
    return message


def buy_new_key_message(period: str, price: int, expire_date: datetime.datetime) -> str:
    """Сообщение при покупке нового ключа за счет баланса"""
    date, time = convert_date_time(expire_date)

    message = f"✅ Поздравляем, Вы купили ключ на <b>{period} мес.</b>!\n" \
              f"С баланса списано {price}р.\n"

    message += f"Дата истечения ключа <b>{time} {date}</b>\n\n" \
               f"Вы всегда можете узнать актуальный статус и срок окончания подписки во вкладке \"{btn.KEYS}\" главного меню " \
               f"или с помощью команды /{cmd.KEYS[0]}"
    return message


def not_enough_balance_message(period: str, price: int, balance: int) -> str:
    """Сообщение при отказе в покупке подписки за счет баланса"""
    message = f"⚠️ Недостаточно средств для покупки/продления подписки на {period} мес.\n" \
              f"Необходимо {price}р., ваш остаток на балансе {balance}р.\n\n" \
              f"Вы можете пополнить баланс на необходимую сумму по кнопке ниже"

    return message