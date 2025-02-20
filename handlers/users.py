from typing import Any

from aiogram import Router, types
from aiogram.filters import Command
from database.orm import AsyncOrm

router = Router()


@router.message(Command("instruction"))
async def start_handler(message: types.Message) -> None:
    await message.answer("Help message")


@router.message(Command("help"))
async def start_handler(message: types.Message) -> None:
    await message.answer("Help message")