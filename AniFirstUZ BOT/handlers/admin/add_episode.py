"""
FSM flow: admin selects an anime by code, then uploads episodes one by one
(episode number -> video file). After saving, the admin can immediately
add the next episode or finish.
"""
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from database import requests as db
from keyboards.admin_kb import admin_menu_kb, cancel_kb
from utils.states import AddEpisodeStates

router = Router(name="add_episode")


@router.message(F.text == "🎬 Episode qo'shish")
async def start_add_episode(message: Message, state: FSMContext) -> None:
    await state.set_state(AddEpisodeStates.waiting_anime_code)
    await message.answer("🔍 Anime kodini kiriting:", reply_markup=cancel_kb())


@router.message(AddEpisodeStates.waiting_anime_code, F.text)
async def process_anime_code(message: Message, state: FSMContext) -> None:
    code = message.text.strip()
    anime = await db.get_anime_by_code(code)
    if not anime:
        await message.answer("⚠️ Bunday kodli anime topilmadi. Qaytadan kiriting:")
        return

    await state.update_data(anime_id=anime.id, anime_name=anime.name)
    await state.set_state(AddEpisodeStates.waiting_episode_number)
    await message.answer(f"✅ Tanlandi: <b>{anime.name}</b>\n\n🔢 Qism raqamini kiriting:")


@router.message(AddEpisodeStates.waiting_episode_number, F.text)
async def process_episode_number(message: Message, state: FSMContext) -> None:
    if not message.text.strip().isdigit():
        await message.answer("⚠️ Iltimos, faqat raqam kiriting.")
        return
    await state.update_data(episode_number=int(message.text.strip()))
    await state.set_state(AddEpisodeStates.waiting_video)
    await message.answer("🎬 Endi video faylni yuboring:")


@router.message(AddEpisodeStates.waiting_video, F.video)
async def process_video(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    episode = await db.add_episode(
        anime_id=data["anime_id"],
        episode_number=data["episode_number"],
        file_id=message.video.file_id,
    )

    await message.answer(
        f"✅ <b>{data['anime_name']}</b> — {episode.episode_number}-qism muvaffaqiyatli qo'shildi!"
    )

    # Allow the admin to keep adding episodes to the same anime quickly.
    await state.set_state(AddEpisodeStates.waiting_episode_number)
    await message.answer("🔢 Keyingi qism raqamini kiriting yoki ❌ Bekor qilish tugmasini bosing:")


@router.message(AddEpisodeStates.waiting_video)
async def invalid_video(message: Message) -> None:
    await message.answer("⚠️ Iltimos, video fayl yuboring.")
