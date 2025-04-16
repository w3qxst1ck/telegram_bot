import datetime
import uuid
from typing import Any

from aiogram import Router, types, F
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext

import schemas.user
from handlers.keyboards import new_key as kb
from logger import logger
from handlers.states.new_key import KeyDescriptionFSM
from handlers.keyboards.balance import not_enough_balance_new_key_keyboard
from handlers.keyboards.menu import to_menu_keyboard
from database.orm import AsyncOrm
from schemas.connection import Connection, Server
from schemas.user import UserConnList
from handlers.messages import new_key as ms
from handlers.messages import errors as err_ms
from handlers.messages.balance import not_enough_balance_message
from services.service import add_client
from cache import r
from settings import settings
from utils.servers_load import get_less_loaded_server

router = Router()


@router.callback_query(F.data == "new_key")
async def choose_country_new_key(callback: types.CallbackQuery, session: Any) -> None:
    """Выбор страны нового ключа"""
    countries = await AsyncOrm.get_server_countries(session)
    msg = ms.choose_country()
    await callback.message.edit_text(msg, reply_markup=kb.new_key_country_keyboard(countries).as_markup())


@router.callback_query(F.data.split("|")[0] == "new_key_country")
async def new_key_menu_handler(callback: types.CallbackQuery, session: Any) -> None:
    """Покупка нового ключа"""
    tg_id = str(callback.from_user.id)
    country = callback.data.split("|")[1]

    user_balance = await AsyncOrm.get_user_balance(tg_id, session)

    msg = ms.new_key_message(user_balance)
    await callback.message.edit_text(msg, reply_markup=kb.new_key_keyboard(country).as_markup())


@router.callback_query(F.data.split("|")[0] == "new_key_period")
async def new_key_confirm_handler(callback: types.CallbackQuery, session: Any) -> None:
    """Подтверждение покупки нового ключа"""
    period = callback.data.split("|")[1]
    country = callback.data.split("|")[2]
    price = settings.price_list[period]
    tg_id = str(callback.from_user.id)

    user_balance = await AsyncOrm.get_user_balance(tg_id, session)

    # достаточно средств
    if user_balance >= price:
        msg = ms.new_key_confirm_message(period, price)
        await callback.message.edit_text(msg, reply_markup=kb.new_key_confirm_keyboard(period, country).as_markup())

    # недостаточно средств на балансе
    else:
        msg = not_enough_balance_message(period, price, user_balance)
        await callback.message.edit_text(msg, reply_markup=not_enough_balance_new_key_keyboard(country).as_markup())


@router.callback_query(F.data.split("|")[0] == "new_key_confirm")
async def create_description(callback: types.CallbackQuery,  state: FSMContext) -> None:
    """Выбор description для ключа, начало KeyDescriptionFSM"""
    period = callback.data.split("|")[1]
    country = callback.data.split("|")[2]
    price = settings.price_list[period]
    tg_id = str(callback.from_user.id)

    await state.set_state(KeyDescriptionFSM.description)
    await state.update_data(period=period)
    await state.update_data(price=price)
    await state.update_data(tg_id=tg_id)
    await state.update_data(country=country)

    msg = ms.key_description()
    prev_mess = await callback.message.edit_text(msg, reply_markup=kb.skip_keyboard().as_markup())
    await state.update_data(prev_mess=prev_mess)


@router.callback_query(F.data.split("|")[0] == "key_description", KeyDescriptionFSM.description)
@router.message(KeyDescriptionFSM.description)
async def new_key_create_handler(callback: types.CallbackQuery | types.Message, state: FSMContext, session: Any) -> None:
    """Обработка подтверждения покупки нового ключа"""

    # получение описания
    if type(callback) == types.CallbackQuery:
        await callback.message.edit_text("Запрос выполняется...⏳")
        description = ""
    else:
        wait_msg = await callback.answer("Запрос выполняется...⏳")
        description = callback.text

    data = await state.get_data()
    period = data["period"]
    price = data["price"]
    tg_id = data["tg_id"]
    country = data["country"]

    # убираем клавиатуру "Пропустить" если название было введено
    if type(callback) == types.Message:
        prev_mess = data.get("prev_mess")
        await prev_mess.edit_text(ms.key_description())

    user_with_conn = await AsyncOrm.get_user_with_connection_list(tg_id, session)

    # добавление клиента в панель
    server_id = await get_less_loaded_server(session, region=country)
    server: Server = await AsyncOrm.get_server(server_id, session)
    email = str(uuid.uuid4())
    key = await add_client(server, email, tg_id)

    # подготовка нового Connection
    if not description:
        description = get_default_description(user_with_conn, server.region)

    # пересчет баланса
    new_balance = user_with_conn.balance - price

    # ключ с описанием после #
    key_with_description = convert_key(key, description)

    new_conn = Connection(
        tg_id=tg_id,
        active=True,
        start_date=datetime.datetime.now(),
        expire_date=datetime.datetime.now() + datetime.timedelta(days=int(period)*30),
        is_trial=False,
        email=email,
        key=key_with_description,
        description=description,
        server_id=server_id
    )

    # создание connection в бд
    try:
        conn_id = await AsyncOrm.buy_new_key(new_conn, new_balance, session)
        msg = ms.buy_new_key_message(period, price, new_conn.expire_date, new_balance, key_with_description)

        # отправка ключа пользователю при пропуске названия
        if type(callback) == types.CallbackQuery:
            await callback.message.edit_text(msg,
                                             reply_markup=to_menu_keyboard().as_markup(),
                                             parse_mode=ParseMode.MARKDOWN)

        # отправка ключа пользователю при введенном названии
        else:
            # удаление сообщения ожидания
            try:
                await wait_msg.delete()
            except TelegramBadRequest:
                pass
            except Exception:
                error_msg = err_ms.general_error_msg()
                await callback.answer(error_msg)

            await callback.answer(msg, reply_markup=to_menu_keyboard().as_markup(), parse_mode=ParseMode.MARKDOWN,
                                  message_effect_id="5046509860389126442")

        # создаем платеж в payments
        await AsyncOrm.create_payment(tg_id, price, f"KEY_{conn_id}", True, datetime.datetime.now(),  session)

        # удаляем кэш
        r.delete(f"user_conn_server:{tg_id}")

        logger.info(f"Пользователь {tg_id} купил новый ключ сроком до {new_conn.expire_date}")

    except Exception:
        error_msg = err_ms.error_msg()
        if type(callback) == types.CallbackQuery:
            await callback.message.edit_text(error_msg, reply_markup=to_menu_keyboard().as_markup())
        else:
            try:
                await wait_msg.delete()
            except Exception:
                pass
            await callback.edit_text(error_msg, reply_markup=to_menu_keyboard().as_markup(), parse_mode=ParseMode.MARKDOWN)
    finally:
        await state.clear()


def convert_key(key: str, description: str) -> str:
    """Убирает стандартный email из названия и добавляет описание"""
    key_without_email = key.split("#")[0] + "#"
    new_description = description.replace(" ", "_")

    return key_without_email + new_description


def get_default_description(user_with_conns: UserConnList, region: str) -> str:
    """Создание автоматического описания"""
    descriptions = [conn.description for conn in user_with_conns.connections]
    new_description = region + f"-{len(user_with_conns.connections)+1}"

    counter = 1
    while new_description in descriptions:
        new_description = region + f"-{len(user_with_conns.connections) + counter}"
        counter += 1

    return new_description
