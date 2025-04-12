from datetime import datetime, timedelta
import uuid
from typing import Any

from aiogram import Router, types, F, Bot
from aiogram.filters import Command, or_f

from middlewares.admin import AdminMiddleware
from database.orm import AsyncOrm
from services import service
from schemas.connection import ServerAdd
from handlers.messages import errors as err_ms
from handlers.messages.balance import paid_request_for_admin, paid_confirmed_for_user, paid_decline_for_user
from utils.servers_load import get_less_loaded_server
from logger import logger


router = Router()
router.message.middleware.register(AdminMiddleware())


@router.message(Command("add_server"))
async def add_server(message: types.Message, session: Any) -> None:
    new_sever = ServerAdd(
        name="am-1",
        region="Netherlands",
        api_url="https://somedomain123.store:2053/jA7PFJItw5/",
        domain="somedomain123.store",
        inbound_id=1,
    )
    await AsyncOrm.create_server(new_sever, session)
    await message.answer("Сервер успешно добавлен")


@router.callback_query(or_f(F.data.split("|")[0] == "admin-payment-confirm",
                            F.data.split("|")[0] == "admin-payment-cancel"))
async def confirm_decline_payment_handler(callback: types.CallbackQuery, bot: Bot, session: Any):
    """Подтверждение или отклонение перевода админом"""
    tg_id = callback.data.split("|")[1]
    summ = callback.data.split("|")[2]
    payment_id = int(callback.data.split("|")[3])

    # подтверждение перевода
    if callback.data.split("|")[0] == "admin-payment-confirm":
        try:
            # подтверждение платежа и пополнение баланса пользователю
            await AsyncOrm.confirm_payment(payment_id, tg_id, int(summ), session)

            # сообщение админу
            message_for_admin = paid_request_for_admin(summ, tg_id).split("\n\n")[0]
            message_for_admin += "\n\nОплата подтверждена ✅\nБаланс пользователя пополнен"
            await callback.message.edit_text(message_for_admin)

            # сообщение пользователю
            message_for_user = paid_confirmed_for_user(summ)
            await bot.send_message(tg_id, message_for_user)

            logger.info(f"Администратор {callback.from_user.id} подтвердил платеж пользователя {tg_id} на сумму {summ} р.")
            logger.info(f"Баланс пользователя {tg_id} пополнен на {summ} р.")
            # TODO Обновить кэш пользователя после пополнения баланса
        except Exception:
            err_msg = err_ms.error_balance_for_admin()
            await callback.message.answer(err_msg)

    # отклонение перевода
    elif callback.data.split("|")[0] == "admin-payment-cancel":
        # сообщение админу
        message_for_admin = paid_request_for_admin(summ, tg_id).split("\n\n")[0]
        message_for_admin += "\n\nОплата отклонена ❌\nОповещение направлено пользователю"
        await callback.message.edit_text(message_for_admin)

        # сообщение пользователю
        message_for_user = paid_decline_for_user(summ)
        await bot.send_message(tg_id, message_for_user)

        logger.info(f"Администратор {callback.from_user.id} отклонил платеж пользователя {tg_id} на сумму {summ} р.")
