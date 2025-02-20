from typing import Any

from aiogram import Router, types
from aiogram.filters import Command
from aiogram.enums import ParseMode
from database.orm import AsyncOrm

router = Router()


@router.message(Command("instruction"))
async def instruction_handler(message: types.Message) -> None:
    # TODO не потерять (копирование текста по нажатию)
    await message.answer("`Instruction message`", parse_mode=ParseMode.MARKDOWN_V2)


@router.message(Command("help"))
async def help_handler(message: types.Message) -> None:
    await message.answer("Help message")