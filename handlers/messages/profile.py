from schemas.user import UserConnection
from utils.date_time_service import convert_date_time
from handlers.buttons import commands as cmd
from handlers.buttons import menu as btn


async def profile_message(user_with_sub: UserConnection) -> str:
    """Сообщение с карточкой профиля"""
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
        message = f"❌ Ваша подписка <b>неактивна</b>\n\n" \
                  f"Вы можете приобрести ее с помощью команды /{cmd.BUY[0]} или в разделе \"{btn.BUY}\" главного меню\n\n"

    # TODO когда будет готова БД
    message += "Какая-то статистика в том числе баланс"
    return message