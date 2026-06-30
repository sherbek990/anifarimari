"""
Async SQLAlchemy engine and session factory.
"""
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from config import config
from database.models import Base

engine = create_async_engine(config.DATABASE_URL, echo=False, future=True)
async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def init_db() -> None:
    """Create all tables if they do not exist yet, and ensure a default settings row exists."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    from database.models import Settings
    async with async_session() as session:
        existing = await session.get(Settings, 1)
        if existing is None:
            session.add(Settings(id=1, force_sub_enabled=True, maintenance_mode=False))
            await session.commit()
