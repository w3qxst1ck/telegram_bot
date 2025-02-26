import datetime
import uuid
from typing import Any

from aiogram import Router, types, F
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

from handlers.buttons import commands as cmd
from handlers.keyboards import buy as buy_kb
from database.orm import AsyncOrm
from schemas.connection import Connection
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

    msg = await ms.buy_message(user_with_conn)

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
@router.callback_query(F.data == "new_key")
async def new_key_menu_handler(callback: types.CallbackQuery, session: Any) -> None:
    """Покупка нового ключа"""
    tg_id = str(callback.from_user.id)

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

    msg = await ms.new_key_message(user_with_conn.balance)
    await callback.message.edit_text(msg, reply_markup=buy_kb.new_key_keyboard().as_markup())


@router.callback_query(F.data.split("|")[0] == "new_key")
async def new_key_confirm_handler(callback: types.CallbackQuery, session: Any) -> None:
    """Подтверждение покупки нового ключа"""
    period = callback.data.split("|")[1]
    price = settings.price_list[period]
    tg_id = str(callback.from_user.id)

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

    # успешная покупка
    if user_with_conn.balance >= price:
        msg = await ms.new_key_confirm_message(period)
        await callback.message.edit_text(msg, reply_markup=buy_kb.new_key_confirm_keyboard(period).as_markup())
    # недостаточно средств на балансе
    else:
        msg = await ms.not_enough_balance_message(period, price, user_with_conn.balance)
        await callback.message.edit_text(msg, reply_markup=buy_kb.not_enough_balance_keyboard().as_markup())


@router.callback_query(F.data.split("|")[0] == "new_key_confirm")
async def new_key_create_handler(callback: types.CallbackQuery, session: Any) -> None:
    """Обработка подтверждения покупки нового ключа"""
    period = callback.data.split("|")[2]
    answer = callback.data.split("|")[1]
    price = settings.price_list[period]
    tg_id = str(callback.from_user.id)

    if answer == "no":
        await new_key_menu_handler(callback, session)
        return
    else:
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

        # подготовка нового Connection
        user_id = 1 # TODO поправить
        email = str(uuid.uuid4())
        key = "SOME KEY FOR TEST" # TODO поправить
        description = "SOME DESCRIPTION" # TODO поправить
        new_balance = user_with_conn.balance - price
        conn = Connection(
            user_id=user_id,
            tg_id=tg_id,
            active=True,
            start_date=datetime.datetime.now(),
            expire_date=datetime.datetime.now() + datetime.timedelta(days=int(period)*30),
            is_trial=False,
            email=email,
            key=key,
            description=description
        )
        await AsyncOrm.buy_new_key(conn, new_balance, session)
        # TODO выписать новый ключ
        # TODO списать с баланса деньги

        msg = await ms.buy_new_key_message(period, price, conn.expire_date)
        await callback.message.edit_text(msg)


@router.callback_query(lambda callback: callback.data == "button_cancel", StateFilter("*"))
async def cancel_handler(callback: types.CallbackQuery, state: FSMContext, session: Any):
    """Cancel FSM and delete last message"""
    await state.clear()
    await buy_handler(callback, session)