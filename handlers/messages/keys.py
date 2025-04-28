import pytz

from schemas.user import UserConnList
from settings import settings
from utils.date_time_service import convert_date_time
from utils.next_refresh_date import get_next_refresh_traffic_date
from handlers.buttons import commands as cmd
from handlers.buttons.regions import REGIONS
from handlers.buttons import menu as btn


def keys_message(user_with_conn: UserConnList) -> str:
    """Сообщение с ключами пользователя"""
    # если есть ключи
    if user_with_conn.connections:
        message = "🔑 ВАШИ КЛЮЧИ\n\n"

        for idx, conn in enumerate(user_with_conn.connections, start=1):
            date, time = convert_date_time(conn.expire_date, with_tz=True)

            # если активна пробная или основная подписка
            if conn.active:

                # если активна пробная подписка
                if conn.is_trial:
                    message += f"*{idx}.* 🎁 *Пробный ключ на {settings.trial_days} дней*\n" \
                               f"🗓️ Активен до *{time} {date} (МСК)*\n" \
                               f"{REGIONS[conn.region]}\n" \
                               f"```{conn.key}```\n\n"

                # если активна основная подписка
                else:
                    refresh_date, _ = convert_date_time(
                        get_next_refresh_traffic_date(conn.start_date), with_tz=True)

                    # если превышен трафик
                    if conn.traffic > settings.traffic_limit:
                        message += f"*{idx}.* ⚠️ Ключ *{conn.description}*\n" \
                                   f"🗓️ Активен до *{time} {date} (МСК)*\n" \
                                   f"{REGIONS[conn.region]}\n" \
                                   f"❗ Превышен лимит трафика: *{conn.traffic} / {settings.traffic_limit}* ГБ (обновление {refresh_date})\n" \
                                   f"```{conn.key}```\n\n"

                    # если трафик в норме
                    else:
                        message += f"*{idx}.* ✅ Ключ *{conn.description}*\n" \
                                   f"🗓️ Активен до *{time} {date} (МСК)*\n" \
                                   f"{REGIONS[conn.region]}\n" \
                                   f"📊 Трафик: *{conn.traffic} / {settings.traffic_limit}* ГБ (обновление {refresh_date})\n" \
                                   f"```{conn.key}```\n\n"

            # если подписка неактивна
            else:
                message += f"*{idx}.* ❌ Ключ {conn.description} *неактивен*\n" \
                           f"{REGIONS[conn.region]}\n" \
                           f"```{conn.key}```\n\n"

        message += f"Нажмите на ключ, чтобы скопировать\n\n"
        message += f"Вы можете продлить ключ с помощью команды /{cmd.BUY[0]} или в разделе \"{btn.BUY}\" главного меню\n\n"
        message += f"Если кончился лимит трафика, вы можете его обновить с помощью кнопки \"{btn.EXTRA_TRAFFIC}\" ниже\n\n"
        message += f"Чтобы удалить ключ, нажмите \"{btn.DELETE_KEY}\" и затем выберите необходимый"

    # если нет ключей
    else:
        message = f"У вас еще нет купленных ключей для подключения VPN. Вы можете купить новый ключ с помощью " \
                  f"команды /{cmd.BUY[0]} или в разделе \"{btn.BUY}\" главного меню"

    return message