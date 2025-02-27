from typing import Any

from aiogram import Router, types, F
from aiogram.filters import Command

from handlers.buttons import commands as cmd
from handlers.keyboards import buy as buy_kb
from database.orm import AsyncOrm
from handlers.messages import buy as ms


router = Router()


@router.message(Command(f"{cmd.BUY[0]}"))
@router.callback_query(F.data.split("|")[1] == "buy")
async def buy_handler(message: types.Message | types.CallbackQuery, session: Any) -> None:
    tg_id = str(message.from_user.id)

    # TODO test version
    user_with_conn = await AsyncOrm.get_user_with_connection_list(tg_id, session)

    # TODO prod version
    # cached_data = r.get(f"profile:{tg_id}")
    # if cached_data:
    #     # from cache
    #     user_with_conn = UserConnList.model_validate_json(cached_data)
    # else:
    #     # from DB
    #     user_with_conn = await AsyncOrm.get_user_with_connection_list(tg_id, session)
    #     user_with_conn_json = user_with_conn.model_dump_json()
    #     r.setex(f"profile:{tg_id}", 300, user_with_conn_json)

    msg = ms.buy_message(user_with_conn)

    if type(message) == types.Message:
        await message.answer(msg, reply_markup=buy_kb.buy_keyboard().as_markup())
    elif type(message) == types.CallbackQuery:
        await message.message.edit_text(msg, reply_markup=buy_kb.buy_keyboard(back_bnt=True).as_markup())
