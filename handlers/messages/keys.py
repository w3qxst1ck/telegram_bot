from schemas.user import UserConnList
from utils.date_time_service import convert_date_time
from handlers.buttons import commands as cmd
from handlers.buttons import menu as btn


def keys_message(user_with_conn: UserConnList) -> str:
    """Сообщение с ключами пользователя"""
    # если есть ключи
    if user_with_conn.connections:
        message = "🔑 ВАШИ КЛЮЧИ\n\n"

        for idx, conn in enumerate(user_with_conn.connections, start=1):
            date, time = convert_date_time(conn.expire_date)

            # если активна пробная или основная подписка
            if conn.active:

                # если активна пробная подписка
                if conn.is_trial:
                    message += f"*{idx}.* ✅ *Пробная подписка на 1 день*\n" \
                               f"🗓️ Активен до *{time} {date}*\n" \
                               f"```{conn.key}```\n\n"

                # если активна основная подписка
                else:
                    message += f"*{idx}.* ✅ Ключ *{conn.email}*\n" \
                               f"🗓️ Активен до *{time} {date}*\n" \
                               f"📊 Траффик за месяц {conn.traffic}Гб\n" \
                               f"```{conn.key}```\n\n"

            # если подписка неактивна
            else:
                message += f"*{idx}.* ❌ Ключ {conn.email} *неактивен*\n" \
                           f"```{conn.key}```\n\n"

        message += f"Нажмите на ключ, чтобы скопировать\n\n"
        message += f"Вы можете продлить ключ с помощью команды /{cmd.BUY[0]} или в разделе \"{btn.BUY}\" главного меню"
        # TODO когда будет готова БД

    # если нет ключей
    else:
        message = f"У вас еще нет купленных ключей для подключения VPN. Вы можете купить новый ключ с помощью" \
                  f"команды /{cmd.BUY[0]} или в разделе \"{btn.BUY}\" главного меню"

    return message