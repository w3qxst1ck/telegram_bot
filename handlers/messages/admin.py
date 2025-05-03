

def statistics_message(data: dict) -> str:
    """Сообщение со статистикой"""
    message = f"📊 Отчёт по статистике\n\n" \
              f"👥 <b>Пользователи:</b> {data['all_users']}\n"\
              f"— Новых за месяц: {data['month_count_users']}\n"\
              f"— С активными ключами: {data['users_with_active_keys']}\n\n"\
              f"🔗 <b>Приглашенные пользователи:</b> {data['referral_users']}\n" \
              f"— Активные: {data['active_referral_users']}\n" \
              f"— Неактивные: {data['referral_users'] - data['active_referral_users']}\n\n" \
              f"🔑 <b>Всего ключей:</b> {data['all_keys']}\n"\
              f"— Активных ключей: {data['active_keys']}\n"\
              f"— Пробных ключей: {data['trial_keys']}\n\n"\
              f"💵 <b>Всего пополнений:</b> {data['payments_transfer_all_time'] + data['payments_stars_all_time']} ₽\n" \
              f"— Переводом: {data['payments_transfer_all_time']} ₽\n" \
              f"— Telegram Stars: {data['payments_stars_all_time']} ₽\n\n"\
              f"📈 <b>Пополнений за месяц:</b> {data['payments_transfer_last_period'] + data['payments_stars_last_period']} ₽\n" \
              f"— Переводом: {data['payments_transfer_last_period']} ₽\n" \
              f"— Telegram Stars: {data['payments_stars_last_period']} ₽\n"

    return message
