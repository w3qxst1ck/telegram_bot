import base64
import aiogram
from aiogram.utils.deep_linking import create_start_link

from settings import settings


async def generate_invite_link(tg_id: str, bot: aiogram.Bot) -> str:
    """Генерирует ссылку приглашение для телеграм"""
    invite_link = await create_start_link(bot, tg_id, encode=True)
    return invite_link


async def decode_invite_link(invite_link: str) -> str:
    """Декодирует ссылку приглашение возвращает tg_id: str"""
    tg_id = base64.b64decode(invite_link.removeprefix(f"https://t.me/{settings.bot_tg_name}?start=")).decode("utf-8")
    return tg_id
