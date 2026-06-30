"""
Keyboards (reply + inline) used in the user-facing part of the bot.
"""
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import config
from database.models import Anime, Channel


def main_menu_kb() -> ReplyKeyboardMarkup:
    kb = [
        [KeyboardButton(text="🔍 Anime qidirish")],
        [KeyboardButton(text="👑 VIP"), KeyboardButton(text="ℹ️ Yordam")],
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


def subscription_kb(channels: list[Channel]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for ch in channels:
        link = ch.invite_link or (f"https://t.me/{ch.username}" if ch.username else "https://t.me/")
        builder.row(InlineKeyboardButton(text=f"➕ {ch.title}", url=link))
    builder.row(InlineKeyboardButton(text="✅ Tekshirish", callback_data="verify_sub"))
    builder.row(InlineKeyboardButton(text="💎 VIP olish", callback_data="get_vip"))
    return builder.as_markup()


def anime_card_kb(anime: Anime, reactions: dict[str, int] | None = None) -> InlineKeyboardMarkup:
    reactions = reactions or {}
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="💎 Tomosha qilish 💎", callback_data=f"watch:{anime.id}:1")
    )
    builder.row(
        InlineKeyboardButton(
            text=f"📥 Yuklash (1-{anime.episodes_count})", callback_data=f"download:{anime.id}"
        )
    )

    reaction_emojis = ["❤️", "🔥", "👍", "💯"]
    reaction_row = [
        InlineKeyboardButton(
            text=f"{emoji} {reactions.get(emoji, 0)}", callback_data=f"react:{anime.id}:{emoji}"
        )
        for emoji in reaction_emojis
    ]
    builder.row(*reaction_row)

    if anime.channel_link:
        builder.row(InlineKeyboardButton(text="📢 Kanal", url=anime.channel_link))

    return builder.as_markup()


def episodes_kb(
    anime_id: int, total_episodes: int, page: int = 1, per_page: int = config.EPISODES_PER_PAGE
) -> InlineKeyboardMarkup:
    """Build a paginated episode-selection keyboard, 5 buttons per row."""
    builder = InlineKeyboardBuilder()

    start = (page - 1) * per_page + 1
    end = min(page * per_page, total_episodes)

    buttons = [
        InlineKeyboardButton(text=str(ep), callback_data=f"episode:{anime_id}:{ep}")
        for ep in range(start, end + 1)
    ]
    builder.row(*buttons, width=config.EPISODES_PER_ROW)

    nav_row = []
    if page > 1:
        nav_row.append(
            InlineKeyboardButton(text="⬅️ Oldingi", callback_data=f"watch:{anime_id}:{page - 1}")
        )
    if end < total_episodes:
        nav_row.append(
            InlineKeyboardButton(text="Keyingi ➡️", callback_data=f"watch:{anime_id}:{page + 1}")
        )
    if nav_row:
        builder.row(*nav_row)

    builder.row(InlineKeyboardButton(text="🔙 Orqaga", callback_data=f"back_to_card:{anime_id}"))
    return builder.as_markup()


def episode_watch_kb(anime_id: int, episode_number: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="🔙 Qismlar ro'yxati", callback_data=f"watch:{anime_id}:1"
        )
    )
    return builder.as_markup()
