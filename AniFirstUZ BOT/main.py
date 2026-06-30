"""
Application entry point. Run with: python main.py
"""
import asyncio
import logging

from database.engine import init_db
from handlers.admin import admin_router
from handlers.users import user_router
from loader import bot, dp
from middlewares.database import DatabaseMiddleware
from middlewares.throttling import ThrottlingMiddleware

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


async def on_startup() -> None:
    await init_db()
    logger.info("Database initialized.")
    me = await bot.get_me()
    logger.info("Bot started as @%s", me.username)


def register_middlewares() -> None:
    dp.message.middleware(ThrottlingMiddleware())
    dp.message.middleware(DatabaseMiddleware())
    dp.callback_query.middleware(DatabaseMiddleware())


def register_routers() -> None:
    # IMPORTANT: admin_router is included first. Its message/callback filters
    # (IsAdmin) cause non-admin updates to fall through to user_router below,
    # while admin updates are handled here first.
    dp.include_router(admin_router)
    dp.include_router(user_router)


async def main() -> None:
    register_middlewares()
    register_routers()
    dp.startup.register(on_startup)

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped.")
