"""
Handles the "✅ Verify" button users press after joining required channels.
"""
from aiogram import Router
from aiogram.types import CallbackQuery

from keyboards.user_kb import main_menu_kb, subscription_kb
from services.subscription import get_unsubscribed_channels

router = Router(name="subscription")


@router.callback_query(lambda c: c.data == "verify_sub")
async def verify_subscription(callback: CallbackQuery) -> None:
    missing = await get_unsubscribed_channels(callback.bot, callback.from_user.id)
    if missing:
        await callback.answer("❌ Siz hali barcha kanallarga obuna bo'lmadingiz!", show_alert=True)
        await callback.message.edit_reply_markup(reply_markup=subscription_kb(missing))
        return

    await callback.answer("✅ Obuna tasdiqlandi!", show_alert=True)
    await callback.message.delete()
    await callback.message.answer(
        "🎉 Tabriklaymiz! Endi botdan to'liq foydalanishingiz mumkin.",
        reply_markup=main_menu_kb(),
    )
