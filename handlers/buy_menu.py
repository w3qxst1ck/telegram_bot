from typing import Any

from aiogram import Router, types, F
from aiogram.filters import Command

from handlers.buttons import commands as cmd
from handlers.keyboards import buy as kb
from database.orm import AsyncOrm
from handlers.messages import buy as ms


router = Router()


@router.message(Command(f"{cmd.BUY[0]}"))
@router.callback_query(F.data.split("|")[1] == "buy")
async def buy_handler(message: types.Message | types.CallbackQuery, session: Any) -> None:
    tg_id = str(message.from_user.id)

    user_balance: int = await AsyncOrm.get_user_balance(tg_id, session)

    msg = ms.buy_message(user_balance)

    if type(message) == types.Message:
        await message.answer(msg, reply_markup=kb.buy_keyboard().as_markup())
    elif type(message) == types.CallbackQuery:
        await message.message.edit_text(msg, reply_markup=kb.buy_keyboard(back_bnt=True).as_markup())
