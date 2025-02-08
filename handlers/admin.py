from typing import Any

from aiogram import Router, types
from aiogram.filters import Command
from logger import logger
from database.orm import AsyncOrm
from schemas.user import UserAdd

router = Router()


@router.message(Command("test"))
async def start_handler(message: types.Message, session: Any) -> None:
    await message.answer("Test world")

