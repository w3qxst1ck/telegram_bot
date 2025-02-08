from typing import Any

from aiogram import Router, types
from aiogram.filters import Command
from database.orm import AsyncOrm
from schemas.user import UserAdd

router = Router()


@router.message(Command("start"))
async def start_handler(message: types.Message, admin: bool, session: Any) -> None:
    tg_id: str = str(message.from_user.id)

    user: UserAdd = UserAdd(
        tg_id=tg_id,
        username=message.from_user.username,
        firstname=message.from_user.first_name,
        lastname=message.from_user.last_name
    )

    await message.answer(f"Hello message. Is admin: {admin}")
    # создание пользователя
    await AsyncOrm.create_user(user, session)
    # создание подписки
    await AsyncOrm.create_subscription(tg_id, session)


@router.message(Command("help"))
async def start_handler(message: types.Message) -> None:
    await message.answer("Help message")