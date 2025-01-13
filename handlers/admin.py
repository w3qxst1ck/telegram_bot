from aiogram import Router, types
from aiogram.filters import Command
from logger import logger

router = Router()


@router.message(Command("start"))
async def start_handler(message: types.Message) -> None:
    logger.debug("Дебаг сообщение")
    logger.info("Инфо сообщение")
    logger.warning("Варнинг сообщение")
    logger.error("Еррор сообщение")
    logger.critical("Критикал сообщение")
    await message.answer("Hello world")


@router.message(Command("help"))
async def start_handler(message: types.Message) -> None:
    await message.answer("Help message")
