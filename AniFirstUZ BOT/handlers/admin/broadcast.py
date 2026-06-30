"""
Broadcast (reklama yuborish): admin sends text/photo/video, previews it,
confirms, then it's sent to every registered user.
"""
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from keyboards.admin_kb import admin_menu_kb, broadcast_confirm_kb, cancel_kb
from services.broadcast import broadcast_message
from utils.states import BroadcastStates

router = Router(name="broadcast")


@router.message(F.text == "📢 Reklama yuborish")
async def start_broadcast(message: Message, state: FSMContext) -> None:
    await state.set_state(BroadcastStates.waiting_content)
    await message.answer(
        "📢 Yubormoqchi bo'lgan xabarni yuboring (matn, rasm yoki video bo'lishi mumkin):",
        reply_markup=cancel_kb(),
    )


@router.message(BroadcastStates.waiting_content)
async def preview_broadcast(message: Message, state: FSMContext) -> None:
    await state.update_data(source_chat_id=message.chat.id, source_message_id=message.message_id)
    await state.set_state(BroadcastStates.waiting_confirm)
    await message.answer("👀 Quyida xabar ko'rinishi (preview):")
    await message.copy_to(chat_id=message.chat.id)
    await message.answer(
        "Ushbu xabarni barcha foydalanuvchilarga yuborishni tasdiqlaysizmi?",
        reply_markup=broadcast_confirm_kb(),
    )


@router.callback_query(BroadcastStates.waiting_confirm, F.data == "broadcast_confirm")
async def confirm_broadcast(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    await state.clear()
    await callback.message.edit_text("📤 Yuborilmoqda, biroz kuting...")

    source_message = await callback.bot.forward_message(
        chat_id=callback.from_user.id,
        from_chat_id=data["source_chat_id"],
        message_id=data["source_message_id"],
        disable_notification=True,
    )
    # We use a forwarded copy as the canonical "source" object purely to reuse copy_to().
    success, fail = await broadcast_message(callback.bot, source_message, callback.from_user.id)
    await source_message.delete()

    await callback.message.answer(
        f"✅ Yuborish yakunlandi!\n\n📨 Muvaffaqiyatli: {success}\n❌ Xato: {fail}",
        reply_markup=admin_menu_kb(),
    )
    await callback.answer()


@router.callback_query(BroadcastStates.waiting_confirm, F.data == "broadcast_cancel")
async def cancel_broadcast(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.edit_text("❌ Reklama yuborish bekor qilindi.")
    await callback.message.answer("⚙️ ADMIN PANEL", reply_markup=admin_menu_kb())
    await callback.answer()
