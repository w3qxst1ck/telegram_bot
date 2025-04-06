from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from handlers.buttons import commands as cmd
from handlers.keyboards import menu as menu_kb
from handlers.messages.users import instruction_message
from handlers.keyboards import users as kb


router = Router()


@router.message(Command(f"{cmd.INSTRUCTION[0]}"))
async def instruction_handler(message: types.Message) -> None:
    """Выбор ОС для инструкции"""
    msg = instruction_message()
    await message.answer(msg, reply_markup=kb.choose_os().as_markup())


@router.callback_query(F.data.split("|")[0] == "instruction")
async def instruction_for_os(callback: types.CallbackQuery) -> None:
    """Инструкции для отдельных ОС"""
    pass


@router.message(Command(f"{cmd.HELP[0]}"))
async def help_handler(message: types.Message) -> None:
    await message.answer("Help message")


@router.message(Command(f"{cmd.MENU[0]}"))
@router.callback_query(F.data == "menu")
async def main_menu(message: types.Message | types.CallbackQuery, admin: bool, state: FSMContext) -> None:
    """Отправка приветственного сообщения"""
    await state.clear()

    name: str = message.from_user.first_name if message.from_user.first_name else message.from_user.username

    msg = f"Рады видеть тебя, <b>{name}</b>!\n\n" \
          f"Пополняйте баланс, покупайте и продлевайте ключи для доступа к VPN"

    if type(message) == types.Message:
        await message.answer(msg, reply_markup=menu_kb.main_menu_keyboard(admin).as_markup())
    else:
        await message.message.edit_text(msg, reply_markup=menu_kb.main_menu_keyboard(admin).as_markup())
