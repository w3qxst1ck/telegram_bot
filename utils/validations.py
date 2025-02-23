from settings import settings


def is_valid_summ(summ: str) -> bool:
    """Проверка валидности суммы"""
    if "." in summ or "," in summ:
        return False
    try:
        result = int(summ)
        if result < settings.price_list['1']:
            return False
    except ValueError:
        return False
    return True