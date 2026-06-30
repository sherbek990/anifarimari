"""
Entry point to the admin panel.
"""
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from keyboards.admin_kb import admin_menu_kb
from keyboards.user_kb import main_menu_kb

router = Router(name="admin_panel")


@router.message(Command("admin"))
async def open_admin_panel(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("⚙️ <b>ADMIN PANEL</b>\n\nKerakli bo'limni tanlang:", reply_markup=admin_menu_kb())


@router.message(F.text == "🔙 Asosiy menyu")
async def back_to_main(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("🏠 Asosiy menyu", reply_markup=main_menu_kb())


@router.message(F.text == "❌ Bekor qilish")
async def cancel_any_state(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("❌ Bekor qilindi.", reply_markup=admin_menu_kb())
