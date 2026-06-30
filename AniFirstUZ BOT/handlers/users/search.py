"""
Anime search handlers: free-text search by name or exact code.
"""
from aiogram import F, Router
from aiogram.types import InlineKeyboardButton, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database import requests as db
from keyboards.user_kb import anime_card_kb, subscription_kb
from services.subscription import get_unsubscribed_channels
from utils.text import anime_card_text

router = Router(name="search")


@router.message(F.text == "🔍 Anime qidirish")
async def prompt_search(message: Message) -> None:
    await message.answer("🔎 Anime nomi yoki kodini kiriting:")


@router.message(F.text & ~F.text.startswith("/"))
async def handle_search_text(message: Message) -> None:
    """Catch-all text handler: treats any plain text (that isn't a known menu
    button, handled elsewhere with higher priority) as a search query."""
    query = message.text.strip()

    missing = await get_unsubscribed_channels(message.bot, message.from_user.id)
    if missing:
        await message.answer(
            "📛 Botdan foydalanish uchun avval quyidagi kanallarga obuna bo'ling:",
            reply_markup=subscription_kb(missing),
        )
        return

    # Try exact code match first.
    anime = await db.get_anime_by_code(query)

    if anime:
        await db.increment_search_count(anime.id)
        reactions = await db.get_reaction_counts(anime.id)
        await message.answer_photo(
            photo=anime.poster,
            caption=anime_card_text(anime),
            reply_markup=anime_card_kb(anime, reactions),
        )
        return

    results = await db.search_anime_by_name(query)
    if not results:
        await message.answer(
            "😔 Hech narsa topilmadi. Iltimos, boshqa nom yoki kod bilan urinib ko'ring."
        )
        return

    if len(results) == 1:
        anime = results[0]
        await db.increment_search_count(anime.id)
        reactions = await db.get_reaction_counts(anime.id)
        await message.answer_photo(
            photo=anime.poster,
            caption=anime_card_text(anime),
            reply_markup=anime_card_kb(anime, reactions),
        )
        return

    # Multiple matches -> let the user pick.
    builder = InlineKeyboardBuilder()
    for a in results:
        builder.row(InlineKeyboardButton(text=f"{a.name} ({a.code})", callback_data=f"open:{a.id}"))
    await message.answer(
        "🔎 Bir nechta natija topildi, birini tanlang:", reply_markup=builder.as_markup()
    )
