from settings import settings


def instruction_message() -> str:
    """Инструкция"""
    message = "Выберите тип операционной системы устройства с помощью кнопок ниже"
    return message


def help_message() -> str:
    """Help сообщение"""
    message = f"По любым вопросам и техническим проблемам вы можете обратиться к администратору @{settings.help_admin}"

    return message
