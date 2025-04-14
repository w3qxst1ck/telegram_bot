import datetime
from typing import Any

from aiogram import Router, types, F, Bot
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from database.orm import AsyncOrm
from handlers.buttons import commands as cmd
from handlers.keyboards import balance as kb
from handlers.keyboards.menu import to_menu_keyboard
from handlers.messages import balance as ms
from handlers.messages import errors as err_ms
from handlers.states.buy import UpBalanceFSM
from settings import settings
from utils.validations import is_valid_summ
from logger import logger


router = Router()


@router.message(Command(f"{cmd.BALANCE[0]}"))
@router.callback_query(F.data == "menu|balance")
async def balance_handler(message: types.CallbackQuery | types.Message, state: FSMContext, session: Any) -> None:
    """Пополнение баланса. Выбор способа оплаты"""
    # сброс state в случае возврата из введенной суммы
    if type(message) == types.CallbackQuery:
        try:
            await state.clear()
        except Exception:
            pass

    tg_id = str(message.from_user.id)

    user_balance = await AsyncOrm.get_user_balance(tg_id, session)

    text = f"💰 Ваш баланс: <b>{user_balance} р.</b>\n\nВыберите способ оплаты"

    if type(message) == types.Message:
        await message.answer(text, reply_markup=kb.choose_payment_method_keyboard(need_back_button=False).as_markup())
    else:
        await message.message.edit_text(text, reply_markup=kb.choose_payment_method_keyboard().as_markup())


@router.callback_query(F.data == "pay_method_transfer")
async def balance_handler(message: types.CallbackQuery, state: FSMContext, session: Any) -> None:
    """Выбор суммы перевода на карту. Начало UpBalanceFSM"""
    tg_id = str(message.from_user.id)

    user_balance = await AsyncOrm.get_user_balance(tg_id, session)

    await state.set_state(UpBalanceFSM.summ)

    text = f"💰 Ваш баланс: <b>{user_balance} р.</b>\n\nВведите сумму, на которую хотите пополнить баланс"

    msg = await message.message.edit_text(text, reply_markup=kb.back_to_choose_payment_method().as_markup())

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
    # в случае не валидной суммы
    if not is_valid_summ(summ):
        msg = await message.answer(f"Указан неверный формат\n\n"
                                   f"Необходимо указать сумму одним <b>числом</b> без букв, знаков препинания "
                                   f"и других специальных символов (например: 300)\n"
                                   f"Сумма не может быть меньше {settings.price_list['1']}",
                                   reply_markup=kb.back_to_choose_payment_method().as_markup())
        await state.update_data(prev_mess=msg)
        return

    await state.clear()

    invoice_message = ms.invoice_message(summ, str(message.from_user.id))
    await message.answer(
        invoice_message,
        reply_markup=kb.payment_confirm_keyboard(summ).as_markup(),
        parse_mode=ParseMode.MARKDOWN_V2
    )


@router.callback_query(F.data.split("|")[0] == "paid")
async def balance_paid_handler(callback: types.CallbackQuery, bot: Bot, session: Any):
    """Подтверждение перевода пользователем"""
    summ = callback.data.split("|")[1]
    tg_id = str(callback.from_user.id)

    # оповещение пользователя
    message_for_user = ms.paid_request_for_user(summ)
    await callback.message.edit_text(message_for_user, reply_markup=to_menu_keyboard().as_markup())

    # создание платежа
    try:
        created_at = datetime.datetime.now()
        payment_id = await AsyncOrm.init_payment(tg_id, int(summ), created_at, "ADD", session)

        # оповещение администратора
        message_for_admin = ms.paid_request_for_admin(summ, tg_id)
        await bot.send_message(
            settings.payment_admin,
            message_for_admin,
            reply_markup=kb.payment_confirm_admin_keyboard(tg_id, summ, payment_id).as_markup()
        )

        logger.info(f"Пользователь {tg_id} подтвердил оплату платежа на сумму {summ} р.")
    except Exception:
        error_msg = err_ms.error_balance_msg()
        await callback.message.edit_text(error_msg, reply_markup=to_menu_keyboard().as_markup())
