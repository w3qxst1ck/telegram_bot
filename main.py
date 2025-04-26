import asyncio
from datetime import datetime

import aiogram as io
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand, BotCommandScopeDefault
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from middlewares.database import DatabaseMiddleware
from middlewares.admin import AdminMiddleware
from settings import settings
from handlers import main_router
from handlers.buttons import commands as cmd
from schedulers import scheduler as scheduler_funcs

from database.database import async_engine
from database.tables import Base


async def set_commands(bot: io.Bot):
    """Перечень команд для бота"""
    commands = [
        BotCommand(command=f"{cmd.START[0]}", description=f"{cmd.START[1]}"),
        BotCommand(command=f"{cmd.MENU[0]}", description=f"{cmd.MENU[1]}"),
        BotCommand(command=f"{cmd.KEYS[0]}", description=f"{cmd.KEYS[1]}"),
        BotCommand(command=f"{cmd.BALANCE[0]}", description=f"{cmd.BALANCE[1]}"),
        BotCommand(command=f"{cmd.BUY[0]}", description=f"{cmd.BUY[1]}"),
        BotCommand(command=f"{cmd.INVITE[0]}", description=f"{cmd.INVITE[1]}"),
        BotCommand(command=f"{cmd.INSTRUCTION[0]}", description=f"{cmd.INSTRUCTION[1]}"),
        BotCommand(command=f"{cmd.HELP[0]}", description=f"{cmd.HELP[1]}"),
    ]

    await bot.set_my_commands(commands, BotCommandScopeDefault())


async def set_description(bot: io.Bot):
    """Описание бота до запуска"""
    await bot.set_my_description(f"Бот предоставляет доступ к VPN с самым совершенным алгоритмом шифрования VLESS\n\n"
                                 f"{settings.trial_days} дней бесплатно\nА затем {settings.price_list['1']}р в месяц")


async def start_bot() -> None:
    """Запуск бота"""
    bot = io.Bot(settings.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await set_commands(bot)
    await set_description(bot)

    storage = MemoryStorage()
    dp = io.Dispatcher(storage=storage)

    # SCHEDULER
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")

    # перевод закончившихся подписок в неактивные, удаление пробных, оплата реф. ссылок
    scheduler.add_job(scheduler_funcs.run_every_hour, trigger="cron", year='*', month='*', day="*", hour="*", minute=0,
                      second=0, start_date=datetime.now(), kwargs={"bot": bot})

    # обновление трафика ключей каждые settings.paid_period
    scheduler.add_job(scheduler_funcs.run_every_day, trigger="cron", year='*', month='*', day="*", hour=1, minute=10,
                      second=0, start_date=datetime.now(), kwargs={"bot": bot})

    scheduler.start()

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
