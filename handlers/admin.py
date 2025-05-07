from typing import Any

import aiogram
from aiogram import Router, types, F, Bot
from aiogram.filters import or_f
from aiogram.fsm.context import FSMContext

from middlewares.admin import AdminMiddleware
from database.orm import AsyncOrm
from schemas.user import UserConnList
from handlers.messages import errors as err_ms
from handlers.messages.admin import statistics_message
from handlers.messages.balance import paid_request_for_admin, paid_confirmed_for_user, paid_decline_for_user
from logger import logger
from cache import r
from handlers.keyboards import admin as kb
from handlers.states.admin import NotifyUsersFSM


router = Router()
router.message.middleware.register(AdminMiddleware())


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
            await bot.send_message(tg_id, message_for_user, message_effect_id="5104841245755180586")    # 🔥

            # обновляем кэш
            cache_data = r.get(f"user_conn_server:{tg_id}")
            if cache_data:
                user_conn_list = UserConnList.model_validate_json(cache_data)
                user_conn_list.balance += int(summ)
                user_conn_list_json = user_conn_list.model_dump_json()
                r.setex(f"user_conn_server:{tg_id}", 180, user_conn_list_json)

            logger.info(f"Администратор {callback.from_user.id} подтвердил платеж пользователя {tg_id} на сумму {summ} р.")
            logger.info(f"Баланс пользователя {tg_id} пополнен на {summ} р.")

        except Exception as e:
            err_msg = err_ms.error_balance_for_admin(e)
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


@router.callback_query(F.data == "menu|admin")
async def admin_menu(callback: types.CallbackQuery) -> None:
    """Меню администратора"""
    msg = "⚙️️ Панель администратора"
    await callback.message.edit_text(msg, reply_markup=kb.admin_keyboard().as_markup())


@router.callback_query(F.data == "notify_users")
async def choose_users(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Выбор группы пользователей для рассылки"""
    # сброс стейта при кнопке назад из отправки сообщения
    current_state = await state.get_state()
    if current_state:
        await state.clear()

    msg = "\"<b>Всем пользователям</b>\" - рассылка сообщения всем пользователям в боте\n\n" \
          "\"<b>Польз. с активными ключами</b>\" - рассылка сообщения пользователям с активными ключами\n\n" \
          "\"<b>Польз. без активных ключей</b>\" - рассылка сообщения пользователям с просроченными ключами"

    await callback.message.edit_text(msg, reply_markup=kb.admin_users_group().as_markup())


@router.callback_query(F.data.split("|")[0] == "users_group")
async def get_message_for_users(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Предложение отправить сообщение для пользователей"""
    users_group = callback.data.split("|")[1]

    await state.set_state(NotifyUsersFSM.text)
    await state.update_data(users_group=users_group)

    msg = "Отправьте в чат сообщение, которое вы бы хотели разослать "
    if users_group == "all":
        msg += "всем пользователям"
    elif users_group == "expired":
        msg += "пользователям, у которых просрочен ключ"
    else:
        msg += "пользователям, имеющим активные ключи"

    prev_mess = await callback.message.edit_text(msg, reply_markup=kb.back_button().as_markup())
    await state.update_data(prev_mess=prev_mess)


@router.message(NotifyUsersFSM.text)
async def notify_users(message: types.Message, state: FSMContext, session: Any, bot: aiogram.Bot) -> None:
    """Рассылка сообщения"""
    data = await state.get_data()

    # если отправлен не текст
    if not message.text:
        try:
            await data["prev_mess"].delete()
        except Exception:
            pass
        msg = await message.answer("Необходимо отправить текст", reply_markup=kb.back_button().as_markup())
        await state.update_data(prev_mess=msg)
        return

    # если отправлен текст
    await state.clear()

    # меняем предыдущее сообщение
    try:
        await data["prev_mess"].delete()
    except Exception:
        pass

    # отправляем заглушку
    wait_message = await message.answer("Рассылка выполняется...⏳")

    # получаем текст с форматированием и группу пользователей
    msg = message.html_text
    users_group = data["users_group"]

    # получаем необходимых пользователей
    user_ids = await get_user_group_ids(users_group, session)

    # выполняем рассылку
    success_message_counter = 0
    for tg_id in user_ids:
        try:
            await bot.send_message(tg_id, msg)
            success_message_counter += 1
        except Exception as e:
            logger.error(f"При рассылке не удалось отправить сообщение пользователю {tg_id}: {e}")

    await wait_message.edit_text(f"✅ Оповещено пользователей: <b>{success_message_counter}</b>")


async def get_user_group_ids(users_group: str, session: Any) -> list[str]:
    """Возвращает список tg_id пользователей"""
    if users_group == "all":
        users_ids = await AsyncOrm.get_all_tg_ids(session)
    elif users_group == "expired":
        users_ids = await AsyncOrm.get_expired_users_tg_ids(session)
    else:
        users_ids = await AsyncOrm.get_active_users_tg_ids(session)

    return users_ids


@router.callback_query(F.data == "stats")
async def statistics(callback: types.CallbackQuery, session: Any) -> None:
    """Вывод статистики по пользователям"""
    # отправляем заглушку
    wait_message = await callback.message.edit_text("Получение статистики...⏳")

    # получаем данные
    data = await AsyncOrm.get_statistic_data(session)

    msg = statistics_message(data)

    await wait_message.edit_text(msg, reply_markup=kb.back_to_admin_menu().as_markup())


