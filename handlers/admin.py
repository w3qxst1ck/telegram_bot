from aiogram import Router, types
from aiogram.filters import Command

router = Router()


@router.message(Command("test"))
async def start_handler(message: types.Message) -> None:
    await message.answer(f"Test world")

