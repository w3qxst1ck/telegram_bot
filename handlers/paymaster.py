import datetime
from typing import Any

from aiogram import Router, types, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import LabeledPrice

from database.orm import AsyncOrm
from handlers.keyboards.menu import to_menu_keyboard
from handlers.messages import errors as err_ms
from handlers.states.buy import UpBalanceFSM
from settings import settings
from logger import logger


router = Router()


# @router.callback_query(F.data == "pay_method_card", UpBalanceFSM.method)
# async def create_invoice_handler(callback: types.CallbackQuery, state: FSMContext) -> None:
#     """Формирование заказа для оплаты"""
#     data = await state.get_data()
#     await state.clear()
#     try:
#         await data["prev_mess"].delete()
#     except Exception:
#         pass
#
#     summ = data["summ"]
#     payment_invoice = create_payment_invoice(int(summ))
#
#     await callback.message.answer_invoice(**payment_invoice)
#     # await callback.message.delete()
#
#
# @router.pre_checkout_query()
# async def pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery, bot: Bot):
#     await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)
#
#
# @router.message(F.successful_payment)
# async def successful_payment(message: types.Message, session: Any):
#     """В случае успешной оплаты по карте"""
#     wait_message = await message.answer("Платеж обрабатывается...⏳")
#
#     tg_id = str(message.from_user.id)
#     summ = message.successful_payment.invoice_payload
#
#     # создание платежа в БД
#     try:
#         created_at = datetime.datetime.now()
#         await AsyncOrm.init_payment(tg_id, int(summ), created_at, "ADD", session)
#         logger.info(f"Пользователь {tg_id} выполнил оплату через платежную систему на сумму {summ} р.")
#
#     except Exception:
#         error_msg = err_ms.error_balance_msg()
#         await wait_message.edit_text(error_msg, reply_markup=to_menu_keyboard().as_markup())
#
#     # пополнение баланса
#     try:
#         # пополнение баланса пользователю
#         await AsyncOrm.confirm_payment(tg_id, int(summ), session)
#
#         # сообщение пользователю
#         message_for_user = f"✅ Ваш баланс пополнен на <b>{summ} р.</b>"
#         await wait_message.edit_text(tg_id, message_for_user)
#
#         logger.info(f"Баланс пользователя пополнен на сумму {summ} р. через платежную систему")
#
#         # TODO Обновить кэш пользователя после пополнения баланса
#     except Exception as e:
#         err_msg = "⚠️ Ошибка при оформлении платежа. Обратитесь в поддержку."
#         await wait_message.edit_text(err_msg)
#         logger.error(f"Ошибка при пополнении баланса после успешного платежа через платежную систему пользователя "
#                      f"{tg_id}: {e}")
#
#
# def create_payment_invoice(summ: int) -> dict:
#     payment_invoice = {
#         "title": "Оплата",
#         "description": f"Пополнение баланса на {summ} р.",
#         "payload": f"{summ}",
#         "currency": "RUB", "provider_token": settings.payment_token,
#         "prices": [LabeledPrice(label="Пополнение", amount=summ * 100)],
#         "protect_content": True,
#     }
#
#     return payment_invoice