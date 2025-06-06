from collections.abc import Awaitable, Callable
from typing import Any

import asyncpg
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from settings import settings


class DatabaseMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        conn = await asyncpg.connect(
            user=settings.db.postgres_user,
            host=settings.db.postgres_host,
            password=settings.db.postgres_password,
            port=settings.db.postgres_port,
            database=settings.db.postgres_db
        )
        try:
            data["session"] = conn
            return await handler(event, data)
        finally:
            await conn.close()