from handlers.buttons import menu as btn
from handlers.buttons import commands as cmd
from settings import settings


def instruction_menu_message() -> str:
    """Инструкция"""
    message = "Выберите тип операционной системы устройства с помощью кнопок ниже"
    return message


def instruction_os_message(os: str) -> str:
    """Инструкция в зависимости от ОС"""
    message = f"💡 Инструкция для подключения VPN на {os}\n\n"
    message += "Для использования ключа VPN вам необходимо скачать одно из следующих приложений:\n"

    if os == "iOS":
        message += "\t• <a href='https://apps.apple.com/ru/app/v2raytun/id6476628951'>v2RayTun</a>\n" \
                   "\t• <a href='https://apps.apple.com/ru/app/v2box-v2ray-client/id6446814690'>V2Box - V2ray Client</a>\n" \
                   "\t• <a href='https://apps.apple.com/ru/app/streisand/id6450534064'>Streisand</a>\n\n"

    elif os == "Android":
        message += "\t• <a href='https://play.google.com/store/apps/details?id=com.v2raytun.android'>v2RayTun</a>\n" \
                   "\t• <a href='https://play.google.com/store/apps/details?id=com.v2ray.ang'>v2rayNG</a>\n" \
                   "\t• <a href='https://github.com/MatsuriDayo/NekoBoxForAndroid'>NekoBox</a> (<a href='https://itdog.info/ustanovka-nekobox-na-android-iz-apk-fajla-nastrojka-podklyuchenij/'>инструкция</a> по установке)\n\n"

    elif os == "macOS":
        message += "\t• <a href='https://apps.apple.com/ru/app/v2box-v2ray-client/id6446814690'>V2Box - V2ray Client</a>\n" \
                   "\t• <a href='https://apps.apple.com/ru/app/streisand/id6450534064'>Streisand</a>\n" \
                   "\t• <a href='https://apps.apple.com/ru/app/foxray/id6448898396'>FoXray</a>\n\n"

    else:
        message += "\t• <a href='https://github.com/LorenEteval/Furious'>Furious</a>\n" \
                   "\t• <a href='https://github.com/InvisibleManVPN/InvisibleMan-XRayClient'>InvisibleMan-XRayClient</a>\n" \
                   "\t• <a href='https://github.com/MatsuriDayo/nekoray/'>Nekoray</a>\n\n"

    message += f"Необходимо скопировать купленный VPN ключ из раздела \"{btn.KEYS}\" главного меню или " \
               f"из списка ключей с помощью команды /{cmd.KEYS[0]}.\n"

    message += "Далее добавляем ключ в установленное ранее приложение.\n\n"

    message += f"Если у вас есть вопросы по покупке/продлению или использованию ключа, напишите в поддержку @{settings.help_admin}"


    return message