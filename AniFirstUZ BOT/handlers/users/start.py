"""
/start command and main menu / help handlers.
"""
from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from keyboards.user_kb import main_menu_kb
from services.subscription import get_unsubscribed_channels
from keyboards.user_kb import subscription_kb

router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    missing = await get_unsubscribed_channels(message.bot, message.from_user.id)
    if missing:
        await message.answer(
            "📛 Botdan foydalanish uchun quyidagi kanallarga obuna bo'ling:",
            reply_markup=subscription_kb(missing),
        )
        return

    await message.answer(
        f"Salom, <b>{message.from_user.full_name}</b>! 👋\n\n"
        "Anime Bot'ga xush kelibsiz. Anime nomi yoki kodini yuborib qidirishni boshlang, "
        "yoki quyidagi tugmalardan foydalaning.",
        reply_markup=main_menu_kb(),
    )


@router.message(F.text == "ℹ️ Yordam")
async def help_handler(message: Message) -> None:
    await message.answer(
        "🤖 <b>Bot qo'llanmasi</b>\n\n"
        "🔍 Anime nomi yoki kodini yuboring — bot mos animeni topadi.\n"
        "💎 Topilgan animeni tomosha qilish uchun tugmani bosing.\n"
        "📥 Yuklash tugmasi orqali qismlarni yuklab olishingiz mumkin.\n"
        "👑 VIP bo'lim orqali premium imkoniyatlarga ega bo'ling."
    )


@router.message(F.text == "🔙 Asosiy menyu")
async def back_to_main_menu(message: Message) -> None:
    await message.answer("🏠 Asosiy menyu", reply_markup=main_menu_kb())
