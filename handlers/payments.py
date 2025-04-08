from typing import Any

from aiogram import Router, F, types

from database.orm import AsyncOrm
from schemas.payments import Payments
from handlers.messages import payments as ms
from handlers.keyboards.payments import back_to_main_menu

router = Router()


@router.callback_query(F.data.split("|")[1] == "payments")
async def user_payments(callback: types.CallbackQuery, session: Any) -> None:
    """Вывод списка пополнений пользователя"""
    tg_id = str(callback.from_user.id)

    payments: list[Payments] = await AsyncOrm.get_user_payments(tg_id, session)
    user_balance: int = await AsyncOrm.get_user_balance(tg_id, session)

    msg = await ms.user_payments_message(payments, user_balance, session)

    await callback.message.edit_text(msg, reply_markup=back_to_main_menu().as_markup())



