import logging
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


def _fix_asyncpg_url(url: str) -> str:
    """asyncpg uses 'ssl' instead of 'sslmode'."""
    return url.replace("sslmode=", "ssl=")


engine = create_async_engine(
    _fix_asyncpg_url(settings.DATABASE_URL),
    echo=False,
    pool_size=5,
    max_overflow=10,
)

async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except Exception as e:
        logger.error("Failed to initialize database: %s", str(e))
        logger.warning("App will start but DB features won't work until DATABASE_URL is configured in .env")
