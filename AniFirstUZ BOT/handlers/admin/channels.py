"""
Handles add/remove of *mandatory subscription* channels, reached from the
Settings section ("⚙️ Sozlamalar" -> manage channels).
"""
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from database import requests as db
from keyboards.admin_kb import admin_menu_kb, cancel_kb
from utils.states import ChannelManageStates

router = Router(name="channels")


@router.message(F.text == "➕ Kanal qo'shish")
async def start_add_channel(message: Message, state: FSMContext) -> None:
    await state.set_state(ChannelManageStates.waiting_channel_id)
    await message.answer(
        "📨 Kanal ID raqamini yuboring (masalan: -1001234567890).\n"
        "Eslatma: bot kanalda admin bo'lishi shart!",
        reply_markup=cancel_kb(),
    )


@router.message(ChannelManageStates.waiting_channel_id, F.text)
async def process_add_channel(message: Message, state: FSMContext) -> None:
    raw = message.text.strip()
    try:
        channel_id = int(raw)
    except ValueError:
        await message.answer("⚠️ Noto'g'ri ID format. Qaytadan kiriting:")
        return

    try:
        chat = await message.bot.get_chat(channel_id)
    except Exception:
        await message.answer(
            "⚠️ Kanal topilmadi yoki bot u yerda admin emas. Qaytadan urinib ko'ring."
        )
        return

    await db.add_channel(
        channel_id=channel_id,
        title=chat.title or "Noma'lum kanal",
        username=chat.username,
        invite_link=chat.invite_link,
    )
    await state.clear()
    await message.answer(f"✅ \"{chat.title}\" kanali qo'shildi.", reply_markup=admin_menu_kb())


@router.message(F.text == "➖ Kanal o'chirish")
async def start_remove_channel(message: Message, state: FSMContext) -> None:
    channels = await db.get_all_channels()
    if not channels:
        await message.answer("📭 Hozircha kanallar yo'q.")
        return

    listing = "\n".join(f"• {ch.title} — <code>{ch.channel_id}</code>" for ch in channels)
    await state.set_state(ChannelManageStates.waiting_channel_to_remove)
    await message.answer(
        f"📋 Kanallar ro'yxati:\n{listing}\n\nO'chirmoqchi bo'lgan kanal ID sini kiriting:",
        reply_markup=cancel_kb(),
    )


@router.message(ChannelManageStates.waiting_channel_to_remove, F.text)
async def process_remove_channel(message: Message, state: FSMContext) -> None:
    try:
        channel_id = int(message.text.strip())
    except ValueError:
        await message.answer("⚠️ Noto'g'ri ID format.")
        return

    removed = await db.remove_channel(channel_id)
    await state.clear()
    if removed:
        await message.answer("✅ Kanal o'chirildi.", reply_markup=admin_menu_kb())
    else:
        await message.answer("⚠️ Bunday kanal topilmadi.", reply_markup=admin_menu_kb())
