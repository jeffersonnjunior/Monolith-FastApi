from collections.abc import AsyncGenerator
from functools import lru_cache

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import Settings, get_settings


@lru_cache
def get_engine() -> AsyncEngine:
    settings = get_settings()
    if settings.db_url.startswith("sqlite+aiosqlite"):
        return create_async_engine(
            settings.db_url,
            echo=settings.db_echo,
            pool_pre_ping=settings.db_pool_pre_ping,
        )

    return create_async_engine(
        settings.db_url,
        echo=settings.db_echo,
        pool_pre_ping=settings.db_pool_pre_ping,
        pool_size=settings.db_pool_size,
        max_overflow=settings.db_max_overflow,
        pool_timeout=settings.db_pool_timeout,
        pool_recycle=settings.db_pool_recycle,
    )


@lru_cache
def get_session_factory() -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(
        bind=get_engine(),
        class_=AsyncSession,
        autoflush=False,
        expire_on_commit=False,
    )


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    session_factory = get_session_factory()
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def check_database_connection() -> None:
    engine = get_engine()
    async with engine.connect() as connection:
        await connection.execute(text("SELECT 1"))


async def close_engine() -> None:
    await get_engine().dispose()
    get_session_factory.cache_clear()
    get_engine.cache_clear()
