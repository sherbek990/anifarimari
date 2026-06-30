"""
SQLAlchemy ORM models for the anime bot.
Designed to work transparently with SQLite (default) or PostgreSQL
(just change DATABASE_URL in .env).
"""
from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    username: Mapped[str | None] = mapped_column(String(64), nullable=True)
    full_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    joined_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    is_vip: Mapped[bool] = mapped_column(Boolean, default=False)
    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False)


class Admin(Base):
    __tablename__ = "admins"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    added_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Anime(Base):
    __tablename__ = "anime"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(256), index=True)
    code: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    poster: Mapped[str] = mapped_column(String(256))  # telegram file_id of poster photo
    genre: Mapped[str] = mapped_column(String(256))
    episodes_count: Mapped[int] = mapped_column(Integer, default=0)
    dubbed_by: Mapped[str] = mapped_column(String(128))
    language: Mapped[str] = mapped_column(String(64))
    channel_link: Mapped[str | None] = mapped_column(String(256), nullable=True)
    views: Mapped[int] = mapped_column(Integer, default=0)
    searches: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    episodes: Mapped[list["Episode"]] = relationship(
        back_populates="anime", cascade="all, delete-orphan", order_by="Episode.episode_number"
    )
    reactions: Mapped[list["Reaction"]] = relationship(
        back_populates="anime", cascade="all, delete-orphan"
    )


class Episode(Base):
    __tablename__ = "episodes"
    __table_args__ = (UniqueConstraint("anime_id", "episode_number", name="uq_anime_episode"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    anime_id: Mapped[int] = mapped_column(ForeignKey("anime.id", ondelete="CASCADE"))
    episode_number: Mapped[int] = mapped_column(Integer)
    file_id: Mapped[str] = mapped_column(String(256))  # telegram video file_id

    anime: Mapped["Anime"] = relationship(back_populates="episodes")


class Channel(Base):
    __tablename__ = "channels"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    channel_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    title: Mapped[str] = mapped_column(String(128))
    username: Mapped[str | None] = mapped_column(String(128), nullable=True)  # without @, for invite link
    invite_link: Mapped[str | None] = mapped_column(String(256), nullable=True)
    is_required: Mapped[bool] = mapped_column(Boolean, default=True)


class VipUser(Base):
    __tablename__ = "vip_users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)  # None = lifetime
    added_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Reaction(Base):
    __tablename__ = "reactions"
    __table_args__ = (UniqueConstraint("anime_id", "user_id", "reaction_type", name="uq_reaction"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    anime_id: Mapped[int] = mapped_column(ForeignKey("anime.id", ondelete="CASCADE"))
    user_id: Mapped[int] = mapped_column(BigInteger)
    reaction_type: Mapped[str] = mapped_column(String(8))  # emoji as string

    anime: Mapped["Anime"] = relationship(back_populates="reactions")


class Settings(Base):
    __tablename__ = "settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    force_sub_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    maintenance_mode: Mapped[bool] = mapped_column(Boolean, default=False)


class BroadcastLog(Base):
    """Optional log of broadcasts sent, useful for stats/debugging."""

    __tablename__ = "broadcast_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sent_by: Mapped[int] = mapped_column(BigInteger)
    sent_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    success_count: Mapped[int] = mapped_column(Integer, default=0)
    fail_count: Mapped[int] = mapped_column(Integer, default=0)
