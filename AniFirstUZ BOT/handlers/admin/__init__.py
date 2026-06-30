from aiogram import Router

from filters.admin import IsAdmin

from . import (
    panel,
    add_anime,
    delete_anime,
    add_episode,
    channels,
    vip_manage,
    broadcast,
    statistics,
    settings,
    channel_post,
)

admin_router = Router(name="admin")
admin_router.message.filter(IsAdmin())
admin_router.callback_query.filter(IsAdmin())

admin_router.include_router(panel.router)
admin_router.include_router(add_anime.router)
admin_router.include_router(delete_anime.router)
admin_router.include_router(add_episode.router)
admin_router.include_router(channels.router)
admin_router.include_router(vip_manage.router)
admin_router.include_router(broadcast.router)
admin_router.include_router(statistics.router)
admin_router.include_router(settings.router)
admin_router.include_router(channel_post.router)
