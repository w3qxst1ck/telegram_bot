from collections.abc import Awaitable, Callable
from typing import Any

import redis
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from settings import settings
from logger import logger


class CacheMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        r = redis.Redis(host='redis', port=settings.redis.redis_port, password=settings.redis.redis_password)
        try:
            response = r.ping()
            if response:
                data["cache"] = r
                return await handler(event, data)
            else:
                logger.error("Не удалось подключиться к Redis.")
        except redis.exceptions.RedisError as e:
            logger.error(f"Ошибка подключения к Redis: {e}")
