

from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext

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
