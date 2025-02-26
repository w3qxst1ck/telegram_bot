from aiogram import Router, F
from aiogram import types
from typing import Any

from aiogram.filters import Command

from database.orm import AsyncOrm
from handlers.messages.profile import profile_message
from cache import r
from schemas.user import UserConnList
from handlers.keyboards import profile as kb
from handlers.buttons import commands as cmd

router = Router()


@router.callback_query(F.data.split("|")[1] == "profile")
@router.message(Command(cmd.PROFILE[0]))
async def profile(message: types.Message | types.CallbackQuery, session: Any):
    """Карточка профиля"""
    tg_id = str(message.from_user.id)

    # todo test version
    user_with_conn = await AsyncOrm.get_user_with_connection_list(tg_id, session)

    # todo prod version
    # cached_data = r.get(f"profile:{tg_id}")
    # if cached_data:
    #     # from cache
    #     user_with_conn = UserConnList.model_validate_json(cached_data)
    # else:
    #     # from DB
    #     user_with_conn = await AsyncOrm.get_user_with_connection_list(tg_id, session)
    #     # user to json (str) for redis storing
    #     user_with_conn_json = user_with_conn.model_dump_json()
    #     r.setex(f"profile:{tg_id}", 300, user_with_conn_json)

    msg = await profile_message(user_with_conn)

    if type(message) == types.Message:
        await message.answer(
            msg,
            reply_markup=kb.profile_keyboard().as_markup()
        )
    elif type(message) == types.CallbackQuery:
        await message.message.edit_text(
            msg,
            reply_markup=kb.profile_keyboard(back_btn=True).as_markup()
        )

