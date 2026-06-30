"""
Bot settings: toggle mandatory subscription, maintenance mode, and entry
point to channel management buttons.
"""
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database import requests as db
from handlers.admin.channels import start_add_channel, start_remove_channel

router = Router(name="settings")


@router.message(F.text == "⚙️ Sozlamalar")
async def show_settings(message: Message) -> None:
    settings = await db.get_settings()
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=f"Majburiy obuna: {'✅ ON' if settings.force_sub_enabled else '❌ OFF'}",
            callback_data="toggle_force_sub",
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=f"Texnik xizmat: {'✅ ON' if settings.maintenance_mode else '❌ OFF'}",
            callback_data="toggle_maintenance",
        )
    )
    builder.row(InlineKeyboardButton(text="➕ Kanal qo'shish", callback_data="goto_add_channel"))
    builder.row(InlineKeyboardButton(text="➖ Kanal o'chirish", callback_data="goto_remove_channel"))
    await message.answer("⚙️ <b>Bot sozlamalari</b>", reply_markup=builder.as_markup())


@router.callback_query(F.data == "toggle_force_sub")
async def toggle_force_sub(callback: CallbackQuery) -> None:
    settings = await db.get_settings()
    await db.update_settings(force_sub_enabled=not settings.force_sub_enabled)
    await show_settings(callback.message)
    await callback.answer("✅ Yangilandi")


@router.callback_query(F.data == "toggle_maintenance")
async def toggle_maintenance(callback: CallbackQuery) -> None:
    settings = await db.get_settings()
    await db.update_settings(maintenance_mode=not settings.maintenance_mode)
    await show_settings(callback.message)
    await callback.answer("✅ Yangilandi")


@router.callback_query(F.data == "goto_add_channel")
async def goto_add_channel(callback: CallbackQuery, state: FSMContext) -> None:
    await start_add_channel(callback.message, state)
    await callback.answer()


@router.callback_query(F.data == "goto_remove_channel")
async def goto_remove_channel(callback: CallbackQuery, state: FSMContext) -> None:
    await start_remove_channel(callback.message, state)
    await callback.answer()
