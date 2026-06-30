"""
Keyboards used in the admin panel.
"""
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder


def admin_menu_kb() -> ReplyKeyboardMarkup:
    kb = [
        [KeyboardButton(text="➕ Anime qo'shish"), KeyboardButton(text="🗑 Anime o'chirish")],
        [KeyboardButton(text="🎬 Episode qo'shish"), KeyboardButton(text="📨 Kanalga post")],
        [KeyboardButton(text="📢 Reklama yuborish"), KeyboardButton(text="👑 VIP boshqarish")],
        [KeyboardButton(text="📊 Statistika"), KeyboardButton(text="⚙️ Sozlamalar")],
        [KeyboardButton(text="🔙 Asosiy menyu")],
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


def cancel_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Bekor qilish")]], resize_keyboard=True
    )


def settings_kb(force_sub: bool, maintenance: bool) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=f"Majburiy obuna: {'✅ ON' if force_sub else '❌ OFF'}",
            callback_data="toggle_force_sub",
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=f"Texnik xizmat: {'✅ ON' if maintenance else '❌ OFF'}",
            callback_data="toggle_maintenance",
        )
    )
    return builder.as_markup()


def vip_menu_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="➕ VIP qo'shish", callback_data="vip_add"))
    builder.row(InlineKeyboardButton(text="➖ VIP o'chirish", callback_data="vip_remove"))
    builder.row(InlineKeyboardButton(text="📋 VIP ro'yxati", callback_data="vip_list"))
    return builder.as_markup()


def broadcast_confirm_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Yuborish", callback_data="broadcast_confirm"),
        InlineKeyboardButton(text="❌ Bekor qilish", callback_data="broadcast_cancel"),
    )
    return builder.as_markup()


def channel_post_kb(channels: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for ch in channels:
        builder.row(
            InlineKeyboardButton(text=ch.title, callback_data=f"post_to:{ch.channel_id}")
        )
    return builder.as_markup()
