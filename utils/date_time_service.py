from datetime import datetime


def convert_date_time(date: datetime) -> (str, str):
    """Перевод даты в формат для вывода"""
    return date.date().strftime("%d.%m.%Y"), date.time().strftime("%H:%M")



