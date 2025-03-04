from datetime import datetime, timedelta
import uuid
from typing import Any

from aiogram import Router, types, F
from aiogram.filters import Command

from services import service
from schemas.connection import ServerAdd
from database.orm import AsyncOrm
from utils.servers_load import get_less_loaded_server


router = Router()


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
