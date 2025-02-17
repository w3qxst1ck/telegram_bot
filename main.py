import asyncio

import aiogram as io
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand, BotCommandScopeDefault

from middlewares.database import DatabaseMiddleware
from middlewares.admin import AdminMiddleware
from settings import settings
from handlers import main_router


async def set_commands(bot: io.Bot):
    """Перечень команд для бота"""
    commands = [
        BotCommand(command="start", description="👨🏻‍💻 Главное меню"),
    ]

    await bot.set_my_commands(commands, BotCommandScopeDefault())


async def set_description(bot: io.Bot):
    """Описание бота до запуска"""
    await bot.set_my_description("Some description")


async def start_bot() -> None:
    """Запуск бота"""
    bot = io.Bot(settings.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await set_commands(bot)
    await set_description(bot)

    storage = MemoryStorage()
    dp = io.Dispatcher(storage=storage)

    # ROUTERS
    dp.include_router(main_router)

    # MIDDLEWARES
    dp.message.middleware(DatabaseMiddleware())
    dp.callback_query.middleware(DatabaseMiddleware())
    dp.message.middleware(AdminMiddleware())
    dp.callback_query.middleware(AdminMiddleware())

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(start_bot())
