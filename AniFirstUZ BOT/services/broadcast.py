"""
Handles broadcasting a message (text/photo/video) to all bot users,
with basic rate-limiting to avoid hitting Telegram flood limits.
"""
import asyncio

from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError, TelegramRetryAfter
from aiogram.types import Message

from database import requests as db


async def broadcast_message(bot: Bot, source_message: Message, admin_id: int) -> tuple[int, int]:
    """Copy `source_message` to every registered (non-blocked) user.

    Returns (success_count, fail_count).
    """
    user_ids = await db.get_all_user_ids()
    success, fail = 0, 0

    for user_id in user_ids:
        try:
            await source_message.copy_to(chat_id=user_id)
            success += 1
        except TelegramRetryAfter as e:
            await asyncio.sleep(e.retry_after)
            try:
                await source_message.copy_to(chat_id=user_id)
                success += 1
            except Exception:
                fail += 1
        except TelegramForbiddenError:
            # User blocked the bot — mark them as blocked so we skip them next time.
            await db.set_user_blocked(user_id, True)
            fail += 1
        except Exception:
            fail += 1

        await asyncio.sleep(0.05)  # gentle throttle, ~20 messages/sec max

    await db.log_broadcast(sent_by=admin_id, success_count=success, fail_count=fail)
    return success, fail
