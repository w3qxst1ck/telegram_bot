from typing import Any

from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.enums import ParseMode

from database.orm import AsyncOrm
from handlers.buttons import commands as cmd
from handlers.keyboards import menu as menu_kb

router = Router()


@router.message(Command(f"{cmd.INSTRUCTION[0]}"))
async def instruction_handler(message: types.Message) -> None:
    # TODO не потерять (копирование текста по нажатию)
    await message.answer("`Instruction message`", parse_mode=ParseMode.MARKDOWN_V2)


@router.message(Command(f"{cmd.HELP[0]}"))
async def help_handler(message: types.Message) -> None:
    await message.answer("Help message")


@router.message(Command(f"{cmd.MENU[0]}"))
@router.callback_query(F.data == "menu")
async def main_menu(message: types.Message | types.CallbackQuery, admin: bool) -> None:
    """Отправка приветственного сообщения"""
    name: str = message.from_user.first_name if message.from_user.first_name else message.from_user.username

    msg = f"Рады видеть тебя, <b>{name}</b>!\n\n" \
          f"Пополняйте баланс и оформляйте подписку для доступа к VPN"

    if type(message) == types.Message:
        await message.answer(msg, reply_markup=menu_kb.main_menu_keyboard(admin).as_markup())
    else:
        await message.message.edit_text(msg, reply_markup=menu_kb.main_menu_keyboard(admin).as_markup())


@router.callback_query(F.data == "trial_key")
async def send_trial_key(message: types.CallbackQuery, session: Any) -> None:
    """Отправка пользователю ключа для пробного периода"""
    tg_id = str(message.from_user.id)

    # получаем ключ
    ui_key = "SOME KEY"    # todo добавить функцию получения ключа через апи 3x-ui

    # активируем пользователю пробную подписку
    await AsyncOrm.activate_trial_subscription(tg_id, session)
    # записываем ключ
    key = await AsyncOrm.create_key(tg_id, ui_key, "trial", session)

    await message.message.answer(
        "Ваш ключ нажмите чтобы скопировать ⬇️\n\n"
        f"`{key}`",
        parse_mode=ParseMode.MARKDOWN_V2
    )
    await message.message.answer(
        f"Инструкцию по установке и настройке VPN вы можете посмотреть здесь /{cmd.INSTRUCTION[0]}",
        reply_markup=menu_kb.to_menu_keyboard().as_markup()
    )
