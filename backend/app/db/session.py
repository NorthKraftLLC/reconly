from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app.config import settings

_engine = None


def get_engine():
    global _engine
    if _engine is None:
        from sqlalchemy.ext.asyncio import create_async_engine

        _engine = create_async_engine(
            settings.DATABASE_URL_ASYNC,
            poolclass=NullPool,
            echo=settings.DEBUG,
        )
    return _engine


async def get_async_session():
    from sqlalchemy.ext.asyncio import AsyncSession

    engine = get_engine()
    factory = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def close_engine():
    global _engine
    if _engine:
        await _engine.dispose()
        _engine = None


# For celery tasks
async_session = None  # Use get_engine() + sessionmaker() directly in tasks
