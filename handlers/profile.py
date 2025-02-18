import time

from aiogram import Router
from aiogram import types
from typing import Any
from database.orm import AsyncOrm
from handlers.messages.profile import profile_message
from cache import r
from schemas.user import UserSubscription
from handlers.keyboards import profile as kb

router = Router()


@router.callback_query(lambda c: c.data == "profile")
async def profile(callback: types.CallbackQuery, session: Any):
    """Карточка профиля"""
    start_time = time.time()

    tg_id = str(callback.from_user.id)

    cached_data = r.get(f"profile:{tg_id}")
    if cached_data:
        # from cache
        user_with_sub = UserSubscription.model_validate_json(cached_data)
        print("From cache")
        print(type(user_with_sub))
    else:
        # get user
        user_with_sub = await AsyncOrm.get_user_with_subscription(tg_id, session)
        # user to json (str) for redis storing
        user_with_sub_json = user_with_sub.model_dump_json()
        print("NOT from cache")
        print(user_with_sub_json)
        # store to redis for 30 sec
        r.setex(f"profile:{tg_id}", 30, user_with_sub_json)

    msg = await profile_message(user_with_sub)
    await callback.message.answer(msg, reply_markup=kb.profile_keyboard(user_with_sub.active).as_markup())

    end_time = time.time()
    print(end_time-start_time)

