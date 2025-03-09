from datetime import datetime, timedelta
import uuid
from typing import Any

from aiogram import Router, types, F, Bot
from aiogram.filters import Command, or_f

from middlewares.admin import AdminMiddleware
from services import service
from schemas.connection import ServerAdd
from handlers.messages import errors as err_ms
from handlers.messages.balance import paid_request_for_admin, paid_confirmed_for_user, paid_decline_for_user
from database.orm import AsyncOrm
from utils.servers_load import get_less_loaded_server


router = Router()
router.message.middleware.register(AdminMiddleware())


@router.message(Command("test"))
async def start_handler(message: types.Message) -> None:
    await message.answer(f"Test world")


@router.callback_query(F.data == "menu|admin")
async def admin_handler(callback: types.CallbackQuery) -> None:
    pass


@router.message(Command("add_client"))
async def add_client(message: types.Message, session: Any) -> None:
    tg_id = str(message.from_user.id)
    new_uuid = str(uuid.uuid4())

    server_id = await get_less_loaded_server(session)
    server = await AsyncOrm.get_server(server_id, session)

    # создаем ключ в панели 3x-ui
    key = await service.add_client(server, new_uuid, tg_id)
    print(key)

    # записываем в базу данных
    await AsyncOrm.create_connection(
        tg_id=tg_id,
        active=True,
        start_date=datetime.now(),
        expire_date=datetime.now() + timedelta(days=1),
        is_trial=False,
        email=new_uuid,
        key=key,
        description=None,
        server_id=server_id,
        session=session,
    )

    await message.answer(f"{key}\n")


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

    # подтверждение перевода
    if callback.data.split("|")[0] == "admin-payment-confirm":
        try:
            # подтверждение платежа и пополнение баланса пользователю
            await AsyncOrm.confirm_payment(tg_id, int(summ), session)

            # сообщение админу
            message_for_admin = paid_request_for_admin(summ, tg_id).split("\n\n")[0]
            message_for_admin += "\n\nОплата подтверждена ✅\nБаланс пользователя пополнен"
            await callback.message.edit_text(message_for_admin)

            # сообщение пользователю
            message_for_user = paid_confirmed_for_user(summ)
            await bot.send_message(tg_id, message_for_user)

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


#
#
# @router.message(Command("get"))
# async def get_client(message: types.Message) -> None:
#     await am_client.login()
#     client = await am_client.get_client(email='kill_rill')
#     await message.answer(f"{client}")
#
#
# @router.message(Command("block"))
# async def block_client(message: types.Message) -> None:
#     tg_id = str(message.from_user.id)
#     await am_client.login()
#     client = await am_client.block_client(email='60188856-c6b5-40ba-9251-1a5a0dd077fe', tg_id=tg_id)
#     await message.answer(f"{client}")
#
#
# @router.message(Command("unblock"))
# async def unblock_client(message: types.Message) -> None:
#     tg_id = str(message.from_user.id)
#     await am_client.login()
#     client = await am_client.activate_client(email='60188856-c6b5-40ba-9251-1a5a0dd077fe', tg_id=tg_id)
#     await message.answer(f"{client}")
#
#
# @router.message(Command("delete"))
# async def delete_client(message: types.Message) -> None:
#     await am_client.login()
#     await am_client.delete_client(email='60188856-c6b5-40ba-9251-1a5a0dd077fe')
#
#
# @router.message(Command("traf"))
# async def delete_client(message: types.Message, session: Any) -> None:
#     server = await AsyncOrm.get_server(1, session)
#     traffic = await get_client_traffic(server, "rzhep")
#     await message.answer(f"Трафик: {traffic}Гб")
