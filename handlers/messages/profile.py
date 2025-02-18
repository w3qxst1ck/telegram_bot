from schemas.user import UserSubscription
from utils.date_time_service import convert_date_time


async def profile_message(user_with_sub: UserSubscription) -> str:
    """Сообщение с карточкой профиля"""
    date, time = convert_date_time(user_with_sub.expire_date)
    if user_with_sub.is_trial:
        message = f"У вас активирована пробная подписка, она истекает {date} в {time}"
    else:
        if user_with_sub.active:
            message = f"Ваша подписка активна до ...."
        else:
            message = f"Ваша подписка неактивна, вы можете приобрести ее по кнопке ниже"
    return message