"""
Auto channel posting: admin picks an anime by code, previews the generated
post, picks a destination channel, and the bot publishes it there.
"""
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database import requests as db
from keyboards.admin_kb import admin_menu_kb, cancel_kb
from keyboards.user_kb import anime_card_kb
from utils.states import ChannelPostStates
from utils.text import channel_post_text

router = Router(name="channel_post")


@router.message(F.text == "📨 Kanalga post")
async def start_channel_post(message: Message, state: FSMContext) -> None:
    await state.set_state(ChannelPostStates.waiting_anime_code)
    await message.answer("🔍 Post qilmoqchi bo'lgan anime kodini kiriting:", reply_markup=cancel_kb())


@router.message(ChannelPostStates.waiting_anime_code, F.text)
async def process_post_code(message: Message, state: FSMContext) -> None:
    anime = await db.get_anime_by_code(message.text.strip())
    if not anime:
        await message.answer("⚠️ Bunday kodli anime topilmadi. Qaytadan kiriting:")
        return

    channels = await db.get_all_channels()
    if not channels:
        await state.clear()
        await message.answer(
            "📭 Hozircha hech qanday kanal qo'shilmagan. Avval Sozlamalar bo'limidan kanal qo'shing.",
            reply_markup=admin_menu_kb(),
        )
        return

    await state.update_data(anime_id=anime.id)
    await state.set_state(ChannelPostStates.waiting_channel_choice)

    builder = InlineKeyboardBuilder()
    for ch in channels:
        builder.row(InlineKeyboardButton(text=ch.title, callback_data=f"postto:{ch.channel_id}"))

    await message.answer_photo(
        photo=anime.poster,
        caption="👀 Post ko'rinishi (preview):\n\n" + channel_post_text(anime),
    )
    await message.answer("📢 Qaysi kanalga joylashtirilsin?", reply_markup=builder.as_markup())


@router.callback_query(ChannelPostStates.waiting_channel_choice, F.data.startswith("postto:"))
async def process_channel_choice(callback: CallbackQuery, state: FSMContext) -> None:
    channel_id = int(callback.data.split(":")[1])
    data = await state.get_data()
    anime = await db.get_anime_by_id(data["anime_id"])

    if not anime:
        await callback.answer("Anime topilmadi.", show_alert=True)
        await state.clear()
        return

    try:
        await callback.bot.send_photo(
            chat_id=channel_id,
            photo=anime.poster,
            caption=channel_post_text(anime),
            reply_markup=anime_card_kb(anime),
        )
    except Exception as e:
        await callback.message.answer(f"❌ Postni yuborishda xatolik: {e}")
        await callback.answer()
        return

    await state.clear()
    await callback.answer("✅ Post muvaffaqiyatli joylandi!", show_alert=True)
    await callback.message.answer("⚙️ ADMIN PANEL", reply_markup=admin_menu_kb())
