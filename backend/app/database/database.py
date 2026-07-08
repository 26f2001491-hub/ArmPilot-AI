from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from app.core.config import get_settings

settings = get_settings()

engine: AsyncEngine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG, future=True)
