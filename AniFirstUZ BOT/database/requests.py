"""
Repository layer: all direct database queries live here so handlers/services
never touch SQLAlchemy sessions directly. Keeps the codebase clean and testable.
"""
from datetime import datetime
from typing import Sequence

from sqlalchemy import delete, func, select, update

from database.engine import async_session
from database.models import (
    Admin,
    Anime,
    BroadcastLog,
    Channel,
    Episode,
    Reaction,
    Settings,
    User,
    VipUser,
)


# ---------------------------------------------------------------------------
# USERS
# ---------------------------------------------------------------------------

async def get_or_create_user(telegram_id: int, username: str | None, full_name: str | None) -> User:
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.telegram_id == telegram_id))
        if user:
            return user
        user = User(telegram_id=telegram_id, username=username, full_name=full_name)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user


async def get_user(telegram_id: int) -> User | None:
    async with async_session() as session:
        return await session.scalar(select(User).where(User.telegram_id == telegram_id))


async def set_user_blocked(telegram_id: int, blocked: bool = True) -> None:
    async with async_session() as session:
        await session.execute(
            update(User).where(User.telegram_id == telegram_id).values(is_blocked=blocked)
        )
        await session.commit()


async def get_all_user_ids() -> list[int]:
    async with async_session() as session:
        result = await session.scalars(select(User.telegram_id).where(User.is_blocked.is_(False)))
        return list(result)


async def count_users() -> int:
    async with async_session() as session:
        return await session.scalar(select(func.count(User.id))) or 0


# ---------------------------------------------------------------------------
# ADMINS
# ---------------------------------------------------------------------------

async def is_admin(telegram_id: int) -> bool:
    from config import config as cfg

    if telegram_id in cfg.ADMIN_IDS:
        return True
    async with async_session() as session:
        admin = await session.scalar(select(Admin).where(Admin.telegram_id == telegram_id))
        return admin is not None


async def add_admin(telegram_id: int) -> None:
    async with async_session() as session:
        exists = await session.scalar(select(Admin).where(Admin.telegram_id == telegram_id))
        if not exists:
            session.add(Admin(telegram_id=telegram_id))
            await session.commit()


async def remove_admin(telegram_id: int) -> None:
    async with async_session() as session:
        await session.execute(delete(Admin).where(Admin.telegram_id == telegram_id))
        await session.commit()


# ---------------------------------------------------------------------------
# ANIME
# ---------------------------------------------------------------------------

async def add_anime(
    name: str,
    code: str,
    poster: str,
    genre: str,
    episodes_count: int,
    dubbed_by: str,
    language: str,
    channel_link: str | None = None,
) -> Anime:
    async with async_session() as session:
        anime = Anime(
            name=name,
            code=code,
            poster=poster,
            genre=genre,
            episodes_count=episodes_count,
            dubbed_by=dubbed_by,
            language=language,
            channel_link=channel_link,
        )
        session.add(anime)
        await session.commit()
        await session.refresh(anime)
        return anime


async def get_anime_by_code(code: str) -> Anime | None:
    async with async_session() as session:
        return await session.scalar(select(Anime).where(Anime.code == code))


async def get_anime_by_id(anime_id: int) -> Anime | None:
    async with async_session() as session:
        return await session.scalar(select(Anime).where(Anime.id == anime_id))


async def search_anime_by_name(query: str, limit: int = 10) -> Sequence[Anime]:
    async with async_session() as session:
        result = await session.scalars(
            select(Anime).where(Anime.name.ilike(f"%{query}%")).limit(limit)
        )
        return result.all()


async def delete_anime_by_code(code: str) -> bool:
    async with async_session() as session:
        anime = await session.scalar(select(Anime).where(Anime.code == code))
        if not anime:
            return False
        await session.delete(anime)
        await session.commit()
        return True


async def delete_anime_by_name(name: str) -> bool:
    async with async_session() as session:
        anime = await session.scalar(select(Anime).where(Anime.name.ilike(name)))
        if not anime:
            return False
        await session.delete(anime)
        await session.commit()
        return True


async def increment_search_count(anime_id: int) -> None:
    async with async_session() as session:
        await session.execute(
            update(Anime).where(Anime.id == anime_id).values(searches=Anime.searches + 1)
        )
        await session.commit()


async def increment_view_count(anime_id: int) -> None:
    async with async_session() as session:
        await session.execute(
            update(Anime).where(Anime.id == anime_id).values(views=Anime.views + 1)
        )
        await session.commit()


async def count_anime() -> int:
    async with async_session() as session:
        return await session.scalar(select(func.count(Anime.id))) or 0


async def sum_searches() -> int:
    async with async_session() as session:
        return await session.scalar(select(func.coalesce(func.sum(Anime.searches), 0))) or 0


async def sum_views() -> int:
    async with async_session() as session:
        return await session.scalar(select(func.coalesce(func.sum(Anime.views), 0))) or 0


# ---------------------------------------------------------------------------
# EPISODES
# ---------------------------------------------------------------------------

async def add_episode(anime_id: int, episode_number: int, file_id: str) -> Episode:
    async with async_session() as session:
        # Upsert-like behaviour: replace file_id if episode number already exists.
        existing = await session.scalar(
            select(Episode).where(
                Episode.anime_id == anime_id, Episode.episode_number == episode_number
            )
        )
        if existing:
            existing.file_id = file_id
            await session.commit()
            await session.refresh(existing)
            return existing

        episode = Episode(anime_id=anime_id, episode_number=episode_number, file_id=file_id)
        session.add(episode)
        await session.commit()
        await session.refresh(episode)

        # Keep anime.episodes_count in sync (use max episode number as the count).
        await session.execute(
            update(Anime)
            .where(Anime.id == anime_id)
            .values(episodes_count=func.greatest(Anime.episodes_count, episode_number))
        )
        await session.commit()
        return episode


async def get_episodes(anime_id: int) -> Sequence[Episode]:
    async with async_session() as session:
        result = await session.scalars(
            select(Episode).where(Episode.anime_id == anime_id).order_by(Episode.episode_number)
        )
        return result.all()


async def get_episode(anime_id: int, episode_number: int) -> Episode | None:
    async with async_session() as session:
        return await session.scalar(
            select(Episode).where(
                Episode.anime_id == anime_id, Episode.episode_number == episode_number
            )
        )


# ---------------------------------------------------------------------------
# CHANNELS (mandatory subscription)
# ---------------------------------------------------------------------------

async def add_channel(channel_id: int, title: str, username: str | None, invite_link: str | None) -> Channel:
    async with async_session() as session:
        channel = Channel(
            channel_id=channel_id, title=title, username=username, invite_link=invite_link
        )
        session.add(channel)
        await session.commit()
        await session.refresh(channel)
        return channel


async def remove_channel(channel_id: int) -> bool:
    async with async_session() as session:
        result = await session.execute(delete(Channel).where(Channel.channel_id == channel_id))
        await session.commit()
        return result.rowcount > 0


async def get_required_channels() -> Sequence[Channel]:
    async with async_session() as session:
        result = await session.scalars(select(Channel).where(Channel.is_required.is_(True)))
        return result.all()


async def get_all_channels() -> Sequence[Channel]:
    async with async_session() as session:
        result = await session.scalars(select(Channel))
        return result.all()


# ---------------------------------------------------------------------------
# VIP
# ---------------------------------------------------------------------------

async def add_vip(telegram_id: int, expires_at: datetime | None = None) -> None:
    async with async_session() as session:
        vip = await session.scalar(select(VipUser).where(VipUser.telegram_id == telegram_id))
        if vip:
            vip.expires_at = expires_at
        else:
            session.add(VipUser(telegram_id=telegram_id, expires_at=expires_at))
        await session.execute(
            update(User).where(User.telegram_id == telegram_id).values(is_vip=True)
        )
        await session.commit()


async def remove_vip(telegram_id: int) -> None:
    async with async_session() as session:
        await session.execute(delete(VipUser).where(VipUser.telegram_id == telegram_id))
        await session.execute(
            update(User).where(User.telegram_id == telegram_id).values(is_vip=False)
        )
        await session.commit()


async def is_vip(telegram_id: int) -> bool:
    async with async_session() as session:
        vip = await session.scalar(select(VipUser).where(VipUser.telegram_id == telegram_id))
        if not vip:
            return False
        if vip.expires_at and vip.expires_at < datetime.utcnow():
            # Expired VIP -> auto-clean.
            await session.delete(vip)
            await session.execute(
                update(User).where(User.telegram_id == telegram_id).values(is_vip=False)
            )
            await session.commit()
            return False
        return True


async def list_vip_users() -> Sequence[VipUser]:
    async with async_session() as session:
        result = await session.scalars(select(VipUser))
        return result.all()


async def count_vip() -> int:
    async with async_session() as session:
        return await session.scalar(select(func.count(VipUser.id))) or 0


# ---------------------------------------------------------------------------
# REACTIONS
# ---------------------------------------------------------------------------

async def add_reaction(anime_id: int, user_id: int, reaction_type: str) -> dict[str, int]:
    """Toggle a reaction for a user and return updated counts per reaction type."""
    async with async_session() as session:
        existing = await session.scalar(
            select(Reaction).where(
                Reaction.anime_id == anime_id,
                Reaction.user_id == user_id,
                Reaction.reaction_type == reaction_type,
            )
        )
        if existing:
            await session.delete(existing)
        else:
            # Remove any other reaction by this user on this anime (one reaction per user).
            await session.execute(
                delete(Reaction).where(
                    Reaction.anime_id == anime_id, Reaction.user_id == user_id
                )
            )
            session.add(Reaction(anime_id=anime_id, user_id=user_id, reaction_type=reaction_type))
        await session.commit()

        result = await session.execute(
            select(Reaction.reaction_type, func.count(Reaction.id))
            .where(Reaction.anime_id == anime_id)
            .group_by(Reaction.reaction_type)
        )
        return {r_type: count for r_type, count in result.all()}


async def get_reaction_counts(anime_id: int) -> dict[str, int]:
    async with async_session() as session:
        result = await session.execute(
            select(Reaction.reaction_type, func.count(Reaction.id))
            .where(Reaction.anime_id == anime_id)
            .group_by(Reaction.reaction_type)
        )
        return {r_type: count for r_type, count in result.all()}


# ---------------------------------------------------------------------------
# SETTINGS
# ---------------------------------------------------------------------------

async def get_settings() -> Settings:
    async with async_session() as session:
        settings = await session.get(Settings, 1)
        if not settings:
            settings = Settings(id=1, force_sub_enabled=True, maintenance_mode=False)
            session.add(settings)
            await session.commit()
            await session.refresh(settings)
        return settings


async def update_settings(**kwargs) -> None:
    async with async_session() as session:
        await session.execute(update(Settings).where(Settings.id == 1).values(**kwargs))
        await session.commit()


# ---------------------------------------------------------------------------
# BROADCAST LOG
# ---------------------------------------------------------------------------

async def log_broadcast(sent_by: int, success_count: int, fail_count: int) -> None:
    async with async_session() as session:
        session.add(BroadcastLog(sent_by=sent_by, success_count=success_count, fail_count=fail_count))
        await session.commit()
