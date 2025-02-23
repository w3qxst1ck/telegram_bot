import datetime
from typing import Any

from aiogram import Router, types, F
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

from handlers.buttons import commands as cmd
from handlers.keyboards import buy as buy_kb
from handlers.keyboards import menu as menu_kb
from database.orm import AsyncOrm
from schemas.user import UserSubscription
from handlers.messages import buy as ms
from handlers.states.buy import UpBalanceFSM
from cache import r
from settings import settings
from utils.validations import is_valid_summ

router = Router()


@router.message(Command(f"{cmd.BUY[0]}"))
@router.callback_query(F.data.split("|")[1] == "buy")
async def buy_handler(message: types.Message | types.CallbackQuery, session: Any) -> None:
    tg_id = str(message.from_user.id)

    cached_data = r.get(f"profile:{tg_id}")
    if cached_data:
        # from cache
        user_with_sub = UserSubscription.model_validate_json(cached_data)
    else:
        # from DB
        user_with_sub = await AsyncOrm.get_user_with_subscription(tg_id, session)
        user_with_sub_json = user_with_sub.model_dump_json()
        r.setex(f"profile:{tg_id}", 300, user_with_sub_json)

    msg = await ms.buy_message(user_with_sub)

    if type(message) == types.Message:
        await message.answer(msg, reply_markup=buy_kb.buy_keyboard().as_markup())
    elif type(message) == types.CallbackQuery:
        await message.message.edit_text(msg, reply_markup=buy_kb.buy_keyboard(back_bnt=True).as_markup())


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
        invoice_message = await ms.invoice_message(summ, str(message.from_user.id))
        await message.answer(
            invoice_message,
            reply_markup=buy_kb.payment_confirm_keyboard().as_markup(),
            parse_mode=ParseMode.MARKDOWN_V2
        )


# BUY SUBSCRIPTION
@router.callback_query(F.data.split("|")[0] == "buy_sub")
async def buy_sub_handler(callback: types.CallbackQuery, session: Any) -> None:
    """Покупка подписки"""


    # TODO подтверждение покупки подписки


    period = callback.data.split("|")[1]
    price = settings.price_list[period]

    tg_id = str(callback.from_user.id)

    cached_data = r.get(f"profile:{tg_id}")
    if cached_data:
        # from cache
        user_with_sub = UserSubscription.model_validate_json(cached_data)
    else:
        # from DB
        user_with_sub = await AsyncOrm.get_user_with_subscription(tg_id, session)
        user_with_sub_json = user_with_sub.model_dump_json()
        r.setex(f"profile:{tg_id}", 300, user_with_sub_json)

    # успешная покупка
    if user_with_sub.balance >= price:
        # продление подписки
        if user_with_sub.active:
            new_expire_date = user_with_sub.expire_date + datetime.timedelta(days=int(period)*30)
        # покупка подписки
        else:
            new_expire_date = datetime.datetime.now() + datetime.timedelta(days=int(period)*30)
        new_balance = user_with_sub.balance - price

        # покупка первый раз
        if user_with_sub.is_trial:
            await AsyncOrm.buy_subscription_first_time(tg_id, new_expire_date, new_balance, session)
        # покупка или продление не первый раз
        else:
            await AsyncOrm.buy_subscription(tg_id, new_expire_date, new_balance, session)

        msg = await ms.buy_subscription_message(period, price, user_with_sub.active, new_expire_date)
        await callback.message.edit_text(msg, reply_markup=menu_kb.to_menu_keyboard().as_markup())

        # обновление кэша
        user_with_sub = await AsyncOrm.get_user_with_subscription(tg_id, session)
        user_with_sub_json = user_with_sub.model_dump_json()
        r.setex(f"profile:{tg_id}", 300, user_with_sub_json)

    # недостаточно средств на балансе
    else:
        msg = await ms.not_enough_balance_message(period, price, user_with_sub)
        await callback.message.edit_text(msg, reply_markup=buy_kb.not_enough_balance_keyboard().as_markup())


@router.callback_query(lambda callback: callback.data == "button_cancel", StateFilter("*"))
async def cancel_handler(callback: types.CallbackQuery, state: FSMContext, session: Any):
    """Cancel FSM and delete last message"""
    await state.clear()
    await buy_handler(callback, session)