

def statistics_message(data: dict) -> str:
    """Сообщение со статистикой"""
    message = f"Всего пользователей в боте: {data['all_users']}\n"\
              f"За 30 дней присоединилось пользователей: {data['month_count_users']}\n"\
              f"Пользователи с активными ключами: {data['users_with_active_keys']}\n\n"\
              f"Всего ключей: {data['all_keys']}\n"\
              f"Пробных ключей: {data['trial_keys']}\n"\
              f"Активных ключей: {data['active_keys']}\n\n"\
              f"Суммарно пополнений: {data['payments_all_time']}\n"\
              f"Пополнений за 30 дней: {data['payments_last_period']}\n"

    return message
