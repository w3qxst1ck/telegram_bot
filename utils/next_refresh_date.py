import datetime

from settings import settings


def get_next_refresh_traffic_date(start_date: datetime.datetime) -> datetime.datetime:
    """Получение следующего дня обновления трафика"""
    today_date = datetime.datetime.now()

    while start_date < today_date:
        start_date += datetime.timedelta(days=settings.paid_period)

    return start_date
