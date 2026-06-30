from aiogram import Router

from . import start, search, anime_card, subscription, vip

user_router = Router(name="users")
user_router.include_router(start.router)
user_router.include_router(subscription.router)
user_router.include_router(vip.router)
user_router.include_router(anime_card.router)
user_router.include_router(search.router)
