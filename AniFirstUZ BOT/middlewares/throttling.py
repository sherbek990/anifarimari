"""
Simple anti-flood (throttling) middleware using an in-memory TTL cache.
Prevents users from spamming the bot with requests.
"""
import time
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, rate_limit: float = 0.7) -> None:
        self.rate_limit = rate_limit
        self._last_call: dict[int, float] = {}

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        tg_user = data.get("event_from_user")
        if tg_user is not None:
            now = time.monotonic()
            last = self._last_call.get(tg_user.id, 0)
            if now - last < self.rate_limit:
                return  # Drop the update silently — user is going too fast.
            self._last_call[tg_user.id] = now
        return await handler(event, data)
