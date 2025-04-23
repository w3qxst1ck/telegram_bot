from settings import settings
from handlers.buttons import commands as cmd, menu as btn


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
        message += "\t• <a href='https://play.google.com/store/apps/details?id=app.hiddify.com'>Hiddify</a>\n" \
                   "\t• <a href='https://play.google.com/store/apps/details?id=com.v2raytun.android'>v2RayTun</a>\n" \
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
               f"из списка ключей с помощью команды /{cmd.KEYS[0]}.\n\n"

    if os == "Android":
        message += "Далее добавляем ключ в установленное ранее приложение (на скриншотах показан пример с приложением \"Hiddify\").\n\n"
    elif os == "iOS":
        message += "Далее добавляем ключ в установленное ранее приложение (на скриншотах показан пример с приложением \"v2RayTun\").\n\n"
    else:
        message += "Далее добавляем ключ в установленное ранее приложение.\n\n"

    message += f"Если у вас есть вопросы по покупке/продлению или использованию ключа, напишите в поддержку @{settings.help_admin}"

    return message


def help_message() -> str:
    """Help сообщение"""
    message = f"Для доступа к VPN, вам необходимо купить VPN ключ 🔑 в разделе /{cmd.BUY[0]}, новым пользователям выдается пробный ключ (сроком на 1 день), он будет отображен в ваших ключах в разделе /{cmd.KEYS[0]} в период его действия\n\n" \
              f"<b>💰Баланс</b>\nПополнить баланс вы можете в разделе /{cmd.BALANCE[0]} двумя способами:\n" \
              f"- переводом по номеру карты\n- оплатить телеграм звездами\n\n" \
              f"<b>💲 Условия и цены</b>\nСтоимость ключа на {settings.paid_period} дней ({settings.traffic_limit} ГБ) составляет {settings.price_list['1']} р. (все тарифы вы можете посмотреть в разделе /{cmd.BUY[0]})\n\n" \
              f"<b>🔑 Ключи</b>\nПолучить информацию о своих ключах (дату окончания оплаченного периода, объем потребленного трафика, страну и сам ключ), а также удалить ключ \"{btn.DELETE_KEY}\" вы можете в разделе /{cmd.KEYS[0]}\n\n" \
              f"<b>🗓️ Продление ключей</b>\nВ разделе /{cmd.BUY[0]} вы можете продлить срок действия выбранного ключа \"{btn.EXTEND_KEY}\" (купленный срок действия ключа будет добавлен к текущему) или купить новый \"{btn.NEW_KEY}\"\n\n" \
              f"<b>📊 Трафик</b>\nВ месяц на каждый ключ выделяется {settings.traffic_limit} ГБ трафика, который автоматически обновляется каждые {settings.paid_period} дней. " \
              f"В случае превышения лимита трафика, ключ будет заблокирован.\nВы можете обновить трафик любого ключа (текущий трафик выбранного ключа будет обнулен) в разделе /{cmd.KEYS[0]} с помощью кнопки \"{btn.EXTRA_TRAFFIC}\", либо дождаться автоматического ежемесячного обновления трафика." \
              f"\nСтоимость обновления трафика - {settings.extra_traffic_price} р. для одного ключа\n\n" \
              f"<b>👥 Реферальная программа</b>\nПригласив друга по реферальной программе, вы получите бонус в размере {settings.ref_bonus} р. при его первом пополнении баланса. Полученные средства вы можете использовать для оплаты своих ключей VPN. Посмотреть свою реферальную ссылку вы можете с помощью команды /{cmd.INVITE[0]}\n\n" \
              f"<b>💡 Установка и настройка</b>\nПодробную инструкцию по установке и настройке VPN для вашего устройства вы можете посмотреть в разделе /{cmd.INSTRUCTION[0]}"

    message += f"\n\n<b>❓ Вопросы</b>\nПо любым возникшим вопросам и техническим проблемам вы можете обратиться к администратору @{settings.help_admin}"

    return message
