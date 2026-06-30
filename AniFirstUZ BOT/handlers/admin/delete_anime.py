"""
FSM flow: admin deletes an anime by name or code.
"""
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from database import requests as db
from keyboards.admin_kb import admin_menu_kb, cancel_kb
from utils.states import DeleteAnimeStates

router = Router(name="delete_anime")


@router.message(F.text == "🗑 Anime o'chirish")
async def start_delete_anime(message: Message, state: FSMContext) -> None:
    await state.set_state(DeleteAnimeStates.waiting_identifier)
    await message.answer(
        "🗑 O'chirmoqchi bo'lgan anime nomini yoki kodini kiriting:", reply_markup=cancel_kb()
    )


@router.message(DeleteAnimeStates.waiting_identifier, F.text)
async def process_delete(message: Message, state: FSMContext) -> None:
    identifier = message.text.strip()

    deleted = await db.delete_anime_by_code(identifier)
    if not deleted:
        deleted = await db.delete_anime_by_name(identifier)

    await state.clear()
    if deleted:
        await message.answer(f"✅ \"{identifier}\" muvaffaqiyatli o'chirildi.", reply_markup=admin_menu_kb())
    else:
        await message.answer(
            f"⚠️ \"{identifier}\" nomli/kodli anime topilmadi.", reply_markup=admin_menu_kb()
        )
