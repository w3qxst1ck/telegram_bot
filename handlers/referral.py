import os

import aiogram
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import BufferedInputFile

from handlers.buttons import commands as cmd
from utils.invite_link import generate_invite_link
from handlers.messages import referral as ms

router = Router()


@router.message(Command(cmd.INVITE[0]))
async def referral_info(message: types.Message, bot: aiogram.Bot) -> None:
    """Отправляет информацию о реферальной программе"""
    tg_id = str(message.from_user.id)

    invite_link = await generate_invite_link(tg_id, bot)
    msg = ms.referral_info_message(invite_link)

    # await message.answer(msg)
    image_path = os.path.join("img", "start.png")
    if os.path.isfile(image_path):
        with open(image_path, "rb") as image_buffer:
            await message.answer_photo(
                photo=BufferedInputFile(image_buffer.read(), filename="start.png"),
                caption=msg,
            )


