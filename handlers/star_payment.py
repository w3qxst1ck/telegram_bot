import datetime
from typing import Any

from aiogram import Router, F, types
from aiogram.filters import or_f
from aiogram.types import LabeledPrice, PreCheckoutQuery

from database.orm import AsyncOrm
from settings import settings
from handlers.keyboards import star_payment as kb
from handlers.messages.errors import general_error_msg
from handlers.messages import star_payment as ms
from logger import logger

router = Router()


@router.callback_query(or_f(F.data == "pay_method_star", F.data == "cancel_star_payment"))
async def balance_handler(callback: types.CallbackQuery, session: Any) -> None:
    """Пополнение баланса. Выбор способа оплаты"""
    tg_id = str(callback.from_user.id)
    user_balance = await AsyncOrm.get_user_balance(tg_id, session)

    msg = f"💰 Ваш баланс: <b>{user_balance} р.</b>\n\nВыберите количество звезд для пополнения"
    if callback.data == "pay_method_star":
        await callback.message.edit_text(msg, reply_markup=kb.choose_star_count_keyboard().as_markup())
    else:
        try:
            await callback.message.delete()
        except Exception:
            pass
        await callback.message.answer(msg, reply_markup=kb.choose_star_count_keyboard().as_markup())


@router.callback_query(F.data.split("|")[0] == "stars")
async def send_star_invoice_handler(callback: types.CallbackQuery) -> None:
    """Отправка invoice для пополнения звездами"""
    # удаляем предыдущее сообщение
    await callback.message.delete()

    stars_count = int(callback.data.split("|")[1])
    # сумма в рублях
    summ = settings.stars_price_list[str(stars_count)]

    await callback.message.answer_invoice(
        title=f"Пополнение баланса на {summ} р.",
        description=f"Стоимость {stars_count} ⭐️",
        prices=[LabeledPrice(label="XTR", amount=stars_count)],
        provider_token="",
        payload=f"{summ}",
        currency="XTR",
        reply_markup=kb.back_to_choose_star_count(stars_count).as_markup()
    )


@router.pre_checkout_query()
async def on_pre_checkout_query(pre_checkout_query: PreCheckoutQuery):
    await pre_checkout_query.answer(ok=True)


@router.message(F.successful_payment)
async def on_successful_payment(message: types.Message, session: Any):
    """Обработка успешного платежа звездами"""
    wait_message = await message.answer("Обработка платежа...⏳")

    summ = int(message.successful_payment.invoice_payload)
    tg_id = str(message.from_user.id)

    # создание записи в payments
    created_at = datetime.datetime.now()
    await AsyncOrm.create_payment(tg_id, summ, "STARS", True, created_at, session)

    # пополнение баланса
    try:
        await AsyncOrm.up_balance(tg_id, summ, session)
    except Exception:
        msg = general_error_msg()
        await wait_message.edit_text(msg)
        return

    msg = ms.up_balance_message(summ)
    # ответ пользователю
    await wait_message.edit_text(msg)

    logger.info(f"Пользователь {tg_id} пополнил баланс звездами на сумму {summ}")



