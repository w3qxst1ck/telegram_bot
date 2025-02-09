import os
from typing import Any

from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, BufferedInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.orm import AsyncOrm
from schemas.user import UserAdd

router = Router()


@router.message(Command("start"))
async def start_handler(message: types.Message, admin: bool, session: Any) -> None:
    tg_id: str = str(message.from_user.id)

    user_exists: bool = await AsyncOrm.check_user_already_exists(tg_id, session)

    if not user_exists:
        user: UserAdd = UserAdd(
            tg_id=tg_id,
            username=message.from_user.username,
            firstname=message.from_user.first_name,
            lastname=message.from_user.last_name
        )
        await AsyncOrm.create_user(user, session)
        await AsyncOrm.create_subscription(tg_id, session)
        await AsyncOrm.create_test_subscription(tg_id, False, False, session)

    await show_start_message(message, admin, session)


async def show_start_message(message: types.Message, admin: bool, session: Any) -> None:
    """Отправка приветственного сообщения"""
    name: str = message.from_user.username if message.from_user.username else message.from_user.first_name
    trial_status = await AsyncOrm.get_trial_subscription_status(str(message.chat.id), session)
    image_path = os.path.join("img", "start.png")

    builder = InlineKeyboardBuilder()

    if not trial_status:
        builder.row(InlineKeyboardButton(text="🔗 Подключить VPN", callback_data="connect-vpn"))

    builder.row(InlineKeyboardButton(text="👤 Личный кабинет", callback_data="profile"))

    builder.row(
        InlineKeyboardButton(text="📞 Поддержка", url="https://www.google.com/webhp?hl=ru&sa=X&ved=0ahUKEwj2iMiEk7eLAxVtVkEAHeEnOj0QPAgI"),
        InlineKeyboardButton(text="🌐 О нашем VPN", callback_data="about"),
    )

    if admin:
        builder.row(InlineKeyboardButton(text="🔧 Администратор", callback_data="admin"))

    if os.path.isfile(image_path):
        with open(image_path, "rb") as image_buffer:
            await message.answer_photo(
                photo=BufferedInputFile(image_buffer.read(), filename="start.png"),
                caption=f"Привет, {name}!\n",
                reply_markup=builder.as_markup(),
            )
    else:
        await message.answer(f"Привет, {name}!\n", reply_markup=builder.as_markup())
