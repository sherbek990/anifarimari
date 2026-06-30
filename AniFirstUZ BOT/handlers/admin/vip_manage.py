"""
VIP management: add, remove, list VIP users.
"""
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from database import requests as db
from keyboards.admin_kb import admin_menu_kb, cancel_kb, vip_menu_kb
from utils.states import VipManageStates

router = Router(name="vip_manage")


@router.message(F.text == "👑 VIP boshqarish")
async def vip_menu(message: Message) -> None:
    await message.answer("👑 VIP boshqaruv bo'limi:", reply_markup=vip_menu_kb())


@router.callback_query(F.data == "vip_add")
async def vip_add_prompt(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(VipManageStates.waiting_add_id)
    await callback.message.answer(
        "➕ VIP qilmoqchi bo'lgan foydalanuvchining Telegram ID sini kiriting:",
        reply_markup=cancel_kb(),
    )
    await callback.answer()


@router.message(VipManageStates.waiting_add_id, F.text)
async def vip_add_process(message: Message, state: FSMContext) -> None:
    if not message.text.strip().lstrip("-").isdigit():
        await message.answer("⚠️ Noto'g'ri ID format.")
        return
    telegram_id = int(message.text.strip())
    await db.add_vip(telegram_id)
    await state.clear()
    await message.answer(f"✅ <code>{telegram_id}</code> endi VIP foydalanuvchi.", reply_markup=admin_menu_kb())


@router.callback_query(F.data == "vip_remove")
async def vip_remove_prompt(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(VipManageStates.waiting_remove_id)
    await callback.message.answer(
        "➖ VIP dan chiqarmoqchi bo'lgan foydalanuvchi ID sini kiriting:", reply_markup=cancel_kb()
    )
    await callback.answer()


@router.message(VipManageStates.waiting_remove_id, F.text)
async def vip_remove_process(message: Message, state: FSMContext) -> None:
    if not message.text.strip().lstrip("-").isdigit():
        await message.answer("⚠️ Noto'g'ri ID format.")
        return
    telegram_id = int(message.text.strip())
    await db.remove_vip(telegram_id)
    await state.clear()
    await message.answer(f"✅ <code>{telegram_id}</code> VIP dan chiqarildi.", reply_markup=admin_menu_kb())


@router.callback_query(F.data == "vip_list")
async def vip_list(callback: CallbackQuery) -> None:
    vips = await db.list_vip_users()
    if not vips:
        await callback.message.answer("📭 Hozircha VIP foydalanuvchilar yo'q.")
    else:
        lines = [f"• <code>{v.telegram_id}</code>" for v in vips]
        await callback.message.answer("👑 VIP foydalanuvchilar:\n" + "\n".join(lines))
    await callback.answer()
