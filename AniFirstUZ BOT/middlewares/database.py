"""
Middleware that ensures every incoming user is registered in the database,
and blocks updates from users who have been banned by an admin.
"""
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User as TgUser

from database import requests as db


class DatabaseMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        tg_user: TgUser | None = data.get("event_from_user")
        if tg_user is not None:
            user = await db.get_or_create_user(
                telegram_id=tg_user.id,
                username=tg_user.username,
                full_name=tg_user.full_name,
            )
            if user.is_blocked:
                return  # Silently ignore blocked users.
            data["db_user"] = user
        return await handler(event, data)
