"""
Shows aggregate bot statistics to admins.
"""
from aiogram import F, Router
from aiogram.types import Message

from database import requests as db
from utils.text import stats_text

router = Router(name="statistics")


@router.message(F.text == "📊 Statistika")
async def show_statistics(message: Message) -> None:
    total_users = await db.count_users()
    total_anime = await db.count_anime()
    total_searches = await db.sum_searches()
    total_views = await db.sum_views()
    vip_count = await db.count_vip()

    await message.answer(
        stats_text(total_users, total_anime, total_searches, total_views, vip_count)
    )
