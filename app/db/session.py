"""Модуль настройки подключения к БД."""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings

engine_settings = {
    'pool_pre_ping': True,
    'pool_size': 2,
    'max_overflow': 4,
    'pool_timeout': 60 * 5,  # 5 минут
    'future': True,
}

Base = declarative_base()

write_engine = create_async_engine(settings.database.database_dsn, **engine_settings)

write_session = sessionmaker(
    write_engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    future=True
)


async def get_db() -> AsyncSession:
    async with write_session() as session:
        yield session
