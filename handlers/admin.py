from typing import Any

from aiogram import Router, types
from aiogram.filters import Command
from logger import logger
from database.orm import AsyncOrm
from schemas.user import UserAdd

router = Router()


@router.message(Command("start"))
async def start_handler(message: types.Message, session: Any) -> None:
    user: UserAdd = UserAdd(
        tg_id=str(message.from_user.id),
        username=message.from_user.username,
        firstname=message.from_user.first_name,
        lastname=message.from_user.last_name
    )

    await AsyncOrm.create_user_test(session, user)
    await message.answer("Hello world")


@router.message(Command("help"))
async def start_handler(message: types.Message) -> None:
    await message.answer("Help message")
