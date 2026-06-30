"""
Handlers for everything that happens after an anime card is shown:
opening from a multi-result list, browsing/paginating episodes, watching
an episode, downloading, and reacting.
"""
from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, InputMediaPhoto

from database import requests as db
from keyboards.user_kb import anime_card_kb, episode_watch_kb, episodes_kb, subscription_kb
from services.subscription import get_unsubscribed_channels
from utils.text import anime_card_text

router = Router(name="anime_card")


@router.callback_query(F.data.startswith("open:"))
async def open_anime(callback: CallbackQuery) -> None:
    anime_id = int(callback.data.split(":")[1])
    anime = await db.get_anime_by_id(anime_id)
    if not anime:
        await callback.answer("Anime topilmadi.", show_alert=True)
        return

    await db.increment_search_count(anime.id)
    reactions = await db.get_reaction_counts(anime.id)
    await callback.message.answer_photo(
        photo=anime.poster,
        caption=anime_card_text(anime),
        reply_markup=anime_card_kb(anime, reactions),
    )
    await callback.answer()


async def _check_access(callback: CallbackQuery) -> bool:
    missing = await get_unsubscribed_channels(callback.bot, callback.from_user.id)
    if missing:
        await callback.answer("❌ Avval kanallarga obuna bo'ling!", show_alert=True)
        await callback.message.answer(
            "📛 Botdan foydalanish uchun quyidagi kanallarga obuna bo'ling:",
            reply_markup=subscription_kb(missing),
        )
        return False
    return True


@router.callback_query(F.data.startswith("watch:"))
async def watch_episodes_list(callback: CallbackQuery) -> None:
    """Shows the paginated episode-number keyboard."""
    if not await _check_access(callback):
        return

    _, anime_id_str, page_str = callback.data.split(":")
    anime_id, page = int(anime_id_str), int(page_str)

    anime = await db.get_anime_by_id(anime_id)
    if not anime:
        await callback.answer("Anime topilmadi.", show_alert=True)
        return

    kb = episodes_kb(anime_id, anime.episodes_count, page=page)
    try:
        await callback.message.edit_caption(
            caption=f"📺 <b>{anime.name}</b>\n\nQism tanlang:", reply_markup=kb
        )
    except TelegramBadRequest:
        await callback.message.answer(f"📺 <b>{anime.name}</b>\n\nQism tanlang:", reply_markup=kb)
    await callback.answer()


@router.callback_query(F.data.startswith("episode:"))
async def send_episode(callback: CallbackQuery) -> None:
    if not await _check_access(callback):
        return

    _, anime_id_str, episode_str = callback.data.split(":")
    anime_id, episode_number = int(anime_id_str), int(episode_str)

    anime = await db.get_anime_by_id(anime_id)
    episode = await db.get_episode(anime_id, episode_number)
    if not anime or not episode:
        await callback.answer("Bu qism topilmadi.", show_alert=True)
        return

    await db.increment_view_count(anime_id)
    await callback.answer("Yuborilmoqda...")
    await callback.message.answer_video(
        video=episode.file_id,
        caption=f"🎬 <b>{anime.name}</b> — {episode_number}-qism",
        reply_markup=episode_watch_kb(anime_id, episode_number),
    )


@router.callback_query(F.data.startswith("download:"))
async def download_episodes(callback: CallbackQuery) -> None:
    if not await _check_access(callback):
        return

    anime_id = int(callback.data.split(":")[1])
    anime = await db.get_anime_by_id(anime_id)
    if not anime:
        await callback.answer("Anime topilmadi.", show_alert=True)
        return

    kb = episodes_kb(anime_id, anime.episodes_count, page=1)
    await callback.answer()
    await callback.message.answer(
        f"📥 <b>{anime.name}</b>\n\nYuklab olish uchun qism raqamini tanlang:", reply_markup=kb
    )


@router.callback_query(F.data.startswith("back_to_card:"))
async def back_to_card(callback: CallbackQuery) -> None:
    anime_id = int(callback.data.split(":")[1])
    anime = await db.get_anime_by_id(anime_id)
    if not anime:
        await callback.answer("Anime topilmadi.", show_alert=True)
        return

    reactions = await db.get_reaction_counts(anime.id)
    try:
        await callback.message.edit_caption(
            caption=anime_card_text(anime), reply_markup=anime_card_kb(anime, reactions)
        )
    except TelegramBadRequest:
        pass
    await callback.answer()


@router.callback_query(F.data.startswith("react:"))
async def react_to_anime(callback: CallbackQuery) -> None:
    _, anime_id_str, emoji = callback.data.split(":")
    anime_id = int(anime_id_str)

    anime = await db.get_anime_by_id(anime_id)
    if not anime:
        await callback.answer("Anime topilmadi.", show_alert=True)
        return

    counts = await db.add_reaction(anime_id, callback.from_user.id, emoji)
    try:
        await callback.message.edit_reply_markup(reply_markup=anime_card_kb(anime, counts))
    except TelegramBadRequest:
        pass
    await callback.answer(f"{emoji} qabul qilindi!")
