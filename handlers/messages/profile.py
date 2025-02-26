from schemas.user import UserConnList
from utils.date_time_service import convert_date_time
from handlers.buttons import commands as cmd
from handlers.buttons import menu as btn


async def profile_message(user_with_conn: UserConnList) -> str:
    """Сообщение с карточкой профиля"""
    # если есть ключи
    if user_with_conn.connections:
        message = "ВАШИ ПОДПИСКИ\n\n"
        # sorted_connection = sorted(user_with_conn.connections, key=lambda c: c.active, reverse=True)

        for idx, conn in enumerate(user_with_conn.connections, start=1):
            date, time = convert_date_time(conn.expire_date)

            # если активна пробная или основная подписка
            if conn.active:

                # если активна пробная подписка
                if conn.is_trial:
                    message += f"<b>{idx}.</b> ✅ <b>Пробная подписка на 1 день</b> активна до <b>{date} {time}</b> " \
                               f"(ключ <i>{conn.email}</i>)\n\n"

                # если активна основная подписка
                else:
                    message += f"<b>{idx}.</b> ✅ <b>Ключ</b> <i>{conn.email}</i> активен до <b>{date} {time}</b>\n" \
                               f"Какая-то инфа по ключу...\n\n"

            # если подписка неактивна
            else:
                message += f"<b>{idx}.</b> ❌ Ключ <i>{conn.email}</i> <b>неактивен</b>\n\n"

        message += f"Вы можете продлить ключ с помощью команды /{cmd.BUY[0]} или в разделе \"{btn.BUY}\" главного меню"
        # TODO когда будет готова БД

    # если нет ключей
    else:
        message = f"У вас еще нет купленных ключей для подключения VPN. Вы можете купить новый ключ с помощью" \
                  f"команды /{cmd.BUY[0]} или в разделе \"{btn.BUY}\" главного меню"

    return message