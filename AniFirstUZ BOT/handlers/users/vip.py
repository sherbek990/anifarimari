"""
VIP info / promotion handlers for regular users.
"""
from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from database import requests as db

router = Router(name="vip")


VIP_INFO_TEXT = (
    "👑 <b>VIP a'zolik</b>\n\n"
    "VIP foydalanuvchilar uchun imkoniyatlar:\n"
    "✅ Majburiy obunasiz foydalanish\n"
    "✅ Reklamasiz tajriba\n"
    "✅ Premium qidiruv filtrlari\n\n"
    "VIP olish uchun administratorga murojaat qiling."
)


@router.message(F.text == "👑 VIP")
async def vip_info(message: Message) -> None:
    is_vip = await db.is_vip(message.from_user.id)
    prefix = "✅ Siz allaqachon VIP foydalanuvchisiz!\n\n" if is_vip else ""
    await message.answer(prefix + VIP_INFO_TEXT)


@router.callback_query(F.data == "get_vip")
async def get_vip_callback(callback: CallbackQuery) -> None:
    await callback.answer()
    await callback.message.answer(VIP_INFO_TEXT)
