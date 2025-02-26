from datetime import datetime


def convert_date_time(date: datetime) -> (str, str):
    """Перевод даты в формат для вывода"""
    return date.date().strftime("%d.%m.%Y"), date.time().strftime("%H:%M")


def convert_date_time_markdown_v2(date: datetime) -> (str, str):
    """Перевод даты в формат для вывода для markdown v2"""
    return date.date().strftime("%d.%m.%Y").replace(".", "\."), date.time().strftime("%H:%M").replace(":", "\.")


