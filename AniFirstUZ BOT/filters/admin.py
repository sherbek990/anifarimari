"""
Custom aiogram filters.
"""
from aiogram.filters import BaseFilter
from aiogram.types import Message

from database import requests as db


class IsAdmin(BaseFilter):
    """Allows the handler to run only if the sender is an admin (env-defined or DB-defined)."""

    async def __call__(self, message: Message) -> bool:
        return await db.is_admin(message.from_user.id)
