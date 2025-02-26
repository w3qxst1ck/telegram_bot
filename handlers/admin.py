import uuid

from aiogram import Router, types, F
from aiogram.filters import Command

from services import service

router = Router()


@router.message(Command("test"))
async def start_handler(message: types.Message) -> None:
    await message.answer(f"Test world")


@router.callback_query(F.data == "menu|admin")
async def admin_handler(callback: types.CallbackQuery) -> None:
    pass


# @router.message(Command("add"))
# async def add_client(message: types.Message) -> None:
#     tg_id = str(message.from_user.id)
#     new_uuid = str(uuid.uuid4())
#     await am_client.login()
#     key = await am_client.add_client(new_uuid, tg_id)
#     print(key)
#     new_client = await am_client.get_client(new_uuid)
#     await message.answer(f"{new_client}\n\n{key}")
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
# async def delete_client(message: types.Message) -> None:
#     await am_client.login()
#     summ = await am_client.get_current_traffic(email='kill_rill')
#     await message.answer(f"{summ}")
