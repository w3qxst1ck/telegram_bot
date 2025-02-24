# import datetime
#
# from settings import settings
# from schemas.user import UserConnection
# from utils.date_time_service import convert_date_time
# from handlers.buttons import menu as btn
# from handlers.buttons import commands as cmd
#
#
# async def buy_message(user_with_sub: UserConnection) -> str:
#     """Сообщение для команды /buy"""
#     date, time = convert_date_time(user_with_sub.expire_date)
#
#     # если активна пробная или основная подписка
#     if user_with_sub.active:
#
#         # если активна пробная подписка
#         if user_with_sub.is_trial:
#             message = f"✅ У вас активирована <b>пробная подписка</b> на 1 день, она истекает {date} в {time}\n\n"
#
#         # если активна основная подписка
#         else:
#             message = f"✅ Ваша подписка активна до <b>{time} {date}</b>\n\n"
#
#     # если подписка неактивна
#     else:
#         message = f"❌ Ваша подписка <b>неактивна</b>\n\n"
#
#     message += f"У вас на балансе <b>{user_with_sub.balance}р</b>\n\n" \
#                f"Стоимость подписки VPN\n" \
#                f"• 1 месяц <b>{settings.price_list['1']}р</b>\n" \
#                f"• 3 месяца <b>{settings.price_list['3']}р</b>\n" \
#                f"• 6 месяцев <b>{settings.price_list['6']}р</b>\n" \
#                f"• 12 месяцев <b>{settings.price_list['12']}р</b>\n\n" \
#                f"Вы можете купить или продлить (оплаченный период будет добавлен к текущему) подписку, " \
#                f"а также пополнить баланс с помощью соответствующих кнопок ниже"
#
#     return message
#
#
# async def invoice_message(summ: str, tg_id: str) -> str:
#     """Сообщение о переводе денег"""
#     message = ""
#     message += f"Для зачисления суммы на баланс необходимо перевести {summ} руб\. по указанным реквизитам \(нажмите, чтобы скопировать реквизиты\)\n\n" \
#                f"`0000 0000 0000 0000`\nАлександр \(Т\-Банк\)\n\n"
#     message += f"❗*ВАЖНО*: \n" \
#                f"В комментарии к оплате для подтверждения платежа укажите число *{tg_id}* для идентификации вашего платежа\.\n\n" \
#                f"После завершения оплаты нажмите кнопку *\"Оплатил\(а\)\"*\."
#     return message
#
#
# async def buy_subscription_message(period: str, price: int, active: bool, expire_date: datetime.datetime) -> str:
#     """Сообщение при покупке подписки за счет баланса"""
#     date, time = convert_date_time(expire_date)
#
#     message = f"✅ Поздравляем, Вы {'продлили' if active else 'купили'} подписку на <b>{period} мес.</b>!\n" \
#               f"С баланса списано {price}р.\n"
#
#     message += f"Дата истечения подписки <b>{time} {date}</b>\n\n" \
#                f"Вы всегда можете узнать актуальный статус и срок окончания подписки во вкладке \"{btn.PROFILE}\" главного меню " \
#                f"или с помощью команды /{cmd.PROFILE[0]}"
#     return message
#
#
# async def not_enough_balance_message(period: str, price: int, user_with_sub: UserSubscription) -> str:
#     """Сообщение при отказе в покупке подписки за счет баланса"""
#     message = f"⚠️ Недостаточно средств для покупки/продления подписки на {period} мес.\n" \
#               f"Необходимо {price}р., ваш остаток на балансе {user_with_sub.balance}р.\n\n" \
#               f"Вы можете пополнить баланс на необходимую сумму по кнопке ниже"
#
#     return message