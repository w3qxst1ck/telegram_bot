from typing import Any

from aiogram import Router, types, F
from aiogram.filters import Command

from database.orm import AsyncOrm
from handlers.buttons import commands as cmd
from handlers.keyboards import menu as menu_kb

router = Router()


@router.message(Command("instruction"))
async def start_handler(message: types.Message) -> None:
    await message.answer("Help message")


@router.message(Command("help"))
async def start_handler(message: types.Message) -> None:
    await message.answer("Help message")


@router.message(Command(f"{cmd.MENU[0]}"))
@router.callback_query(F.data == "main_menu")
async def main_menu(message: types.Message | types.CallbackQuery, admin: bool) -> None:
    """Отправка приветственного сообщения"""
    name: str = message.from_user.first_name if message.from_user.first_name else message.from_user.username

    msg = f"Рады видеть тебя, <b>{name}</b>!\n\n" \
          f"Пополняйте баланс и оформляйте подписку для доступа к VPN"
    await message.answer(msg, reply_markup=menu_kb.main_menu_keyboard(admin).as_markup())

