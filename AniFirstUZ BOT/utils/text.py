"""
Text-formatting helpers for building consistent, pretty messages.
"""
from database.models import Anime


def anime_card_text(anime: Anime) -> str:
    return (
        f"✨ <b>{anime.name}</b> ✨\n\n"
        f"📦 Qismlar soni: <b>{anime.episodes_count}</b>\n"
        f"🖊 Janri: <b>{anime.genre}</b>\n"
        f"🎙 Ovoz berdi: <b>{anime.dubbed_by}</b>\n"
        f"☁️ Tili: <b>{anime.language}</b>\n"
        f"🔍 Kod: <code>{anime.code}</code>\n\n"
        f"👁 Ko'rishlar: {anime.views} | 🔎 Qidiruvlar: {anime.searches}"
    )


def channel_post_text(anime: Anime) -> str:
    return (
        f"✨ <b>{anime.name}</b> ✨\n\n"
        f"📦 Qismlar soni: <b>{anime.episodes_count}</b>\n"
        f"🖊 Janri: <b>{anime.genre}</b>\n"
        f"🎙 Ovoz berdi: <b>{anime.dubbed_by}</b>\n"
        f"☁️ Tili: <b>{anime.language}</b>\n"
        f"🔍 Kod: <code>{anime.code}</code>"
    )


def stats_text(
    total_users: int,
    total_anime: int,
    total_searches: int,
    total_views: int,
    vip_count: int,
) -> str:
    return (
        "📊 <b>Bot statistikasi</b>\n\n"
        f"👤 Jami foydalanuvchilar: <b>{total_users}</b>\n"
        f"🎞 Jami anime: <b>{total_anime}</b>\n"
        f"🔎 Jami qidiruvlar: <b>{total_searches}</b>\n"
        f"👁 Jami ko'rishlar: <b>{total_views}</b>\n"
        f"👑 VIP foydalanuvchilar: <b>{vip_count}</b>"
    )
