"""
FSM flow: admin adds a new anime entry (poster -> name -> genre -> episodes
count -> dubbed_by -> language -> code -> optional channel link -> confirm).
"""
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from database import requests as db
from keyboards.admin_kb import admin_menu_kb, cancel_kb
from utils.states import AddAnimeStates
from utils.text import anime_card_text

router = Router(name="add_anime")


@router.message(F.text == "➕ Anime qo'shish")
async def start_add_anime(message: Message, state: FSMContext) -> None:
    await state.set_state(AddAnimeStates.poster)
    await message.answer("🖼 Anime posterini (rasm) yuboring:", reply_markup=cancel_kb())


@router.message(AddAnimeStates.poster, F.photo)
async def process_poster(message: Message, state: FSMContext) -> None:
    await state.update_data(poster=message.photo[-1].file_id)
    await state.set_state(AddAnimeStates.name)
    await message.answer("📝 Anime nomini kiriting:")


@router.message(AddAnimeStates.poster)
async def invalid_poster(message: Message) -> None:
    await message.answer("⚠️ Iltimos, rasm (poster) yuboring.")


@router.message(AddAnimeStates.name, F.text)
async def process_name(message: Message, state: FSMContext) -> None:
    await state.update_data(name=message.text.strip())
    await state.set_state(AddAnimeStates.genre)
    await message.answer("🖊 Janrini kiriting (masalan: Isekai, Sarguzasht, Komediya):")


@router.message(AddAnimeStates.genre, F.text)
async def process_genre(message: Message, state: FSMContext) -> None:
    await state.update_data(genre=message.text.strip())
    await state.set_state(AddAnimeStates.episodes_count)
    await message.answer("📦 Jami qismlar sonini kiriting (raqam):")


@router.message(AddAnimeStates.episodes_count, F.text)
async def process_episodes_count(message: Message, state: FSMContext) -> None:
    if not message.text.strip().isdigit():
        await message.answer("⚠️ Iltimos, faqat raqam kiriting.")
        return
    await state.update_data(episodes_count=int(message.text.strip()))
    await state.set_state(AddAnimeStates.dubbed_by)
    await message.answer("🎙 Kim tomonidan dublyaj qilingan:")


@router.message(AddAnimeStates.dubbed_by, F.text)
async def process_dubbed_by(message: Message, state: FSMContext) -> None:
    await state.update_data(dubbed_by=message.text.strip())
    await state.set_state(AddAnimeStates.language)
    await message.answer("☁️ Tilini kiriting (masalan: O'zbek):")


@router.message(AddAnimeStates.language, F.text)
async def process_language(message: Message, state: FSMContext) -> None:
    await state.update_data(language=message.text.strip())
    await state.set_state(AddAnimeStates.code)
    await message.answer("🔍 Noyob kodini kiriting (masalan: 209):")


@router.message(AddAnimeStates.code, F.text)
async def process_code(message: Message, state: FSMContext) -> None:
    code = message.text.strip()
    existing = await db.get_anime_by_code(code)
    if existing:
        await message.answer("⚠️ Bu kod allaqachon band. Boshqa kod kiriting:")
        return
    await state.update_data(code=code)
    await state.set_state(AddAnimeStates.channel_link)
    await message.answer(
        "📢 Kanal linkini kiriting (ixtiyoriy, o'tkazib yuborish uchun /skip yuboring):"
    )


@router.message(AddAnimeStates.channel_link, F.text)
async def process_channel_link(message: Message, state: FSMContext) -> None:
    link = None if message.text.strip() == "/skip" else message.text.strip()
    await state.update_data(channel_link=link)

    data = await state.get_data()
    anime = await db.add_anime(
        name=data["name"],
        code=data["code"],
        poster=data["poster"],
        genre=data["genre"],
        episodes_count=data["episodes_count"],
        dubbed_by=data["dubbed_by"],
        language=data["language"],
        channel_link=link,
    )
    await state.clear()

    await message.answer_photo(
        photo=anime.poster,
        caption="✅ Anime muvaffaqiyatli qo'shildi!\n\n" + anime_card_text(anime),
    )
    await message.answer("⚙️ ADMIN PANEL", reply_markup=admin_menu_kb())
