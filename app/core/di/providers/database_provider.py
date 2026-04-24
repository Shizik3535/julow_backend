from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config.database_settings import DatabaseSettings


def create_db_engine(settings: DatabaseSettings) -> AsyncEngine:
    """
    Создаёт async SQLAlchemy engine.

    Аргументы:
        settings: Настройки базы данных.
    """
    return create_async_engine(
        settings.url,
        echo=settings.echo,
        pool_size=settings.pool_min_size,
        max_overflow=settings.pool_max_size,
        pool_pre_ping=True,
    )


def create_db_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """
    Создаёт фабрику async сессий SQLAlchemy.

    Аргументы:
        engine: Async SQLAlchemy engine.
    """
    return async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


async def get_db_session(
    session_factory: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[AsyncSession, None]:
    """
    Зависимость FastAPI для получения async сессии БД.

    Автоматически закрывает сессию после использования.
    """
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
