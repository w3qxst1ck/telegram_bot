from settings import settings


def referral_info_message(invite_link: str) -> str:
    message = f"Пригласив друга по реферальной программе, вы получите {settings.ref_bonus} " \
              f"рублей при его первом пополнении баланса.\n\n" \
              f"Полученные средства вы можете использовать для оплаты своих ключей VPN.\n\n" \
              f"Ваша реферальная ссылка, которую вы сможете отправлять друзьям:\n\n" \
              f"<i>👇Нажмите, чтобы скопировать</i>\n\n" \
              f"<code>{invite_link}</code>"

    return message
