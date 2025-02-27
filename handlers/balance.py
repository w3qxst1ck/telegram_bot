from typing import Any

from aiogram import Router, types, F
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext

from handlers.keyboards import buy as buy_kb
from database.orm import AsyncOrm
from schemas.connection import Connection
from handlers.messages import buy as ms
from handlers.states.buy import UpBalanceFSM
from handlers.buy_menu import buy_handler
from cache import r
from settings import settings
from utils.validations import is_valid_summ


router = Router()


# BALANCE
@router.callback_query(F.data == "balance")
async def balance_handler(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Пополнение баланса. Начало UpBalanceFSM"""
    await state.set_state(UpBalanceFSM.summ)

    text = "Введите сумму, на которую хотите пополнить баланс"
    msg = await callback.message.edit_text(text, reply_markup=buy_kb.cancel_keyboard().as_markup())
    await state.update_data(prev_mess=msg)


@router.message(UpBalanceFSM.summ)
async def confirm_up_balance_handler(message: types.Message, state: FSMContext) -> None:
    """Подтверждение пополнения баланса. Конец UpBalanceFSM"""
    data = await state.get_data()
    try:
        await data["prev_mess"].delete()
    except TelegramBadRequest:
        pass

    summ = message.text
    if not is_valid_summ(summ):
        msg = await message.answer(f"Указан неверный формат\n\n"
                                   f"Необходимо указать сумму одним <b>числом</b> без букв, знаков препинания "
                                   f"и других специальных символов (например: 300)\n"
                                   f"Сумма не может быть меньше {settings.price_list['1']}",
                                   reply_markup=buy_kb.cancel_keyboard().as_markup())
        await state.update_data(prev_mess=msg)
        return
    else:
        await state.clear()
        invoice_message = ms.invoice_message(summ, str(message.from_user.id))
        await message.answer(
            invoice_message,
            reply_markup=buy_kb.payment_confirm_keyboard().as_markup(),
            parse_mode=ParseMode.MARKDOWN_V2
        )


@router.callback_query(lambda callback: callback.data == "button_cancel", StateFilter("*"))
async def cancel_handler(callback: types.CallbackQuery, state: FSMContext, session: Any):
    """Cancel FSM and delete last message"""
    await state.clear()
    await buy_handler(callback, session)