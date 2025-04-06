from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from handlers.buttons import commands as cmd
from handlers.keyboards import menu as menu_kb
from handlers.messages import users as ms
from handlers.keyboards import users as kb


router = Router()


@router.message(Command(f"{cmd.INSTRUCTION[0]}"))
@router.callback_query(F.data == "back_to_instruction_menu")
async def instruction_handler(message: types.Message | types.CallbackQuery) -> None:
    """Выбор ОС для инструкции"""
    msg = ms.instruction_menu_message()

    if type(message) == types.Message:
        await message.answer(msg, reply_markup=kb.choose_os().as_markup())
    else:
        await message.message.edit_text(msg, reply_markup=kb.choose_os().as_markup())


@router.callback_query(F.data.split("|")[0] == "instruction")
async def instruction_for_os(callback: types.CallbackQuery) -> None:
    """Инструкции для отдельных ОС"""
    os = callback.data.split("|")[1]

    msg = ms.instruction_os_message(os)

    await callback.message.edit_text(
        msg,
        reply_markup=kb.back_to_instruction_menu().as_markup(),
        disable_web_page_preview=True
    )


@router.message(Command(f"{cmd.HELP[0]}"))
async def help_handler(message: types.Message) -> None:
    msg = ms.help_message()
    await message.answer(msg)


@router.message(Command(f"{cmd.MENU[0]}"))
@router.callback_query(F.data == "menu")
async def main_menu(message: types.Message | types.CallbackQuery, admin: bool, state: FSMContext) -> None:
    """Отправка приветственного сообщения"""
    try:
        await state.clear()
    except:
        pass

    name: str = message.from_user.first_name if message.from_user.first_name else message.from_user.username

    msg = f"Рады видеть тебя, <b>{name}</b>!\n\n" \
          f"Пополняйте баланс, покупайте и продлевайте ключи для доступа к VPN"

    if type(message) == types.Message:
        await message.answer(msg, reply_markup=menu_kb.main_menu_keyboard(admin).as_markup())
    else:
        await message.message.edit_text(msg, reply_markup=menu_kb.main_menu_keyboard(admin).as_markup())
