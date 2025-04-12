from typing import Any

from aiogram import Router, types, F

from logger import logger
from handlers.keyboards import delete_key as kb
from database.orm import AsyncOrm
from schemas.connection import Connection, ConnectionServer
from handlers.messages import delete_key as ms
from handlers.messages import errors as err_ms
from cache import r
from schemas.user import UserConnList
from handlers.keyboards.menu import to_menu_keyboard
from services import service


router = Router()


@router.callback_query(F.data == "delete_key")
async def delete_key_menu(callback: types.CallbackQuery, session: Any) -> None:
    """Меню выбора какой ключ удалить"""
    tg_id = str(callback.from_user.id)

    # TODO test version
    user_with_conns = await AsyncOrm.get_user_with_connection_list(tg_id, session, need_trial=False)

    # TODO prod version
    # cached_data = r.get(f"extend_key:{tg_id}")
    # if cached_data:
    #     # from cache
    #     user_with_conn = UserConnList.model_validate_json(cached_data)
    # else:
    #     # from DB
    #     user_with_conn = await AsyncOrm.get_user_with_connection_list(tg_id, session, need_trial=False)
    #     user_with_conn_json = user_with_conn.model_dump_json()
    #     r.setex(f"extend_key:{tg_id}", 300, user_with_conn_json)

    msg = ms.delete_key_menu(user_with_conns)

    await callback.message.edit_text(msg, reply_markup=kb.delete_key_menu_keyboard(user_with_conns).as_markup())


@router.callback_query(F.data.split("|")[0] == "delete_key_email")
async def delete_key_confirmation(callback: types.CallbackQuery, session: Any) -> None:
    """Подтверждение удаления выбранного ключа"""
    email = callback.data.split("|")[1]

    # TODO cache
    conn_server = await AsyncOrm.get_connection_server(email, session)
    msg = ms.confirm_delete_key(conn_server)

    await callback.message.edit_text(msg, reply_markup=kb.confirm_delete_keyboard(conn_server.email).as_markup())


@router.callback_query(F.data.split("|")[0] == "delete_key_confirm")
async def delete_key(callback: types.CallbackQuery, session: Any) -> None:
    """Удаление ключа"""
    wait_msg = await callback.message.edit_text("Запрос выполняется...⏳")

    email = callback.data.split("|")[1]

    try:
        # TODO cache

        # удаление с панели
        conn_server = await AsyncOrm.get_connection_server(email, session)
        server = await AsyncOrm.get_server(conn_server.server_id, session)
        await service.delete_client(server, email)

        # удаление с БД
        await AsyncOrm.delete_connection(email, session)

        # сообщение об удалении
        msg = ms.key_deleted()
        await wait_msg.edit_text(msg, reply_markup=to_menu_keyboard().as_markup())

        logger.info(f"Пользователь {callback.from_user.id} удалил ключ {email}")

        # TODO refresh cache

    except Exception:
        err_msg = err_ms.general_error_msg()
        await callback.message.edit_text(err_msg)


