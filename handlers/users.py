import aiogram
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile
from aiogram.utils.deep_linking import create_start_link
from aiogram.utils.media_group import MediaGroupBuilder

from handlers.buttons import commands as cmd
from handlers.keyboards import menu as menu_kb
from handlers.messages import users as ms
from handlers.keyboards import users as kb

router = Router()


@router.message(Command(f"{cmd.INSTRUCTION[0]}"))
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
    wait_msg = await callback.message.edit_text("Запрос выполняется...⏳")

    os = callback.data.split("|")[1]

    msg = ms.instruction_os_message(os)

    if os == "Android":
        album_builder = MediaGroupBuilder(caption=msg)
        album_builder.add(type="photo", media=FSInputFile("img/instruction/add_hiddify.jpg"))
        album_builder.add(type="photo", media=FSInputFile("img/instruction/buffer_hiddify.jpg"))
        await callback.message.answer_media_group(media=album_builder.build())
    elif os == "iOS":
        album_builder = MediaGroupBuilder(caption=msg)
        album_builder.add(type="photo", media=FSInputFile("img/instruction/ios_add.PNG"))
        album_builder.add(type="photo", media=FSInputFile("img/instruction/ios_buffer.PNG"))
        await callback.message.answer_media_group(media=album_builder.build())
    # без картинок
    else:
        await callback.message.answer(msg, disable_web_page_preview=True)

    # удаляем заглушку
    try:
        await wait_msg.delete()
    except Exception:
        pass


@router.message(Command(f"{cmd.HELP[0]}"))
async def help_handler(message: types.Message) -> None:
    msg = ms.help_message()
    await message.answer(msg)


@router.message(Command(f"{cmd.MENU[0]}"))
@router.callback_query(F.data == "menu")
async def main_menu(
        message: types.Message | types.CallbackQuery,
        admin: bool,
        state: FSMContext,
        bot: aiogram.Bot
) -> None:
    """Отправка приветственного сообщения"""
    try:
        await state.clear()
    except:
        pass

    name: str = message.from_user.first_name if message.from_user.first_name else message.from_user.username

    tg_id = str(message.from_user.id)
    invite_link = await create_start_link(bot, tg_id, encode=True)

    msg = f"Рады видеть тебя, <b>{name}</b>!\n\n" \
          "<i>Твоя ссылка для приглашения</i>\n" \
          "<i>(нажми на ссылку, чтобы скопировать)</i>\n" \
          f"<code>{invite_link}</code>\n\n" \
          f"Пополняйте баланс, покупайте и продлевайте ключи для доступа к VPN"

    if type(message) == types.Message:
        await message.answer(msg, reply_markup=menu_kb.main_menu_keyboard(admin).as_markup())
    else:
        await message.message.edit_text(msg, reply_markup=menu_kb.main_menu_keyboard(admin).as_markup())
