"""
Handles mandatory-subscription logic: checking whether a user is a member
of all required channels, with VIP users bypassing the check.
"""
from aiogram import Bot

from database import requests as db
from database.models import Channel


async def get_unsubscribed_channels(bot: Bot, user_id: int) -> list[Channel]:
    """Return the list of required channels the user has NOT joined yet."""
    settings = await db.get_settings()
    if not settings.force_sub_enabled:
        return []

    if await db.is_vip(user_id):
        return []

    required = await db.get_required_channels()
    if not required:
        return []

    missing: list[Channel] = []
    for channel in required:
        try:
            member = await bot.get_chat_member(chat_id=channel.channel_id, user_id=user_id)
            if member.status in ("left", "kicked"):
                missing.append(channel)
        except Exception:
            # If the bot can't check (e.g. not admin in that channel), fail safe
            # and require it, so admins notice and fix the channel configuration.
            missing.append(channel)
    return missing


async def is_subscribed(bot: Bot, user_id: int) -> bool:
    missing = await get_unsubscribed_channels(bot, user_id)
    return len(missing) == 0
