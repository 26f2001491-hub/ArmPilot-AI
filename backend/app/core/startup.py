from fastapi import FastAPI

from app.core.config import get_settings
from app.core.logger import get_logger

# Importing the models package registers every table on Base.metadata.
from app import models  # noqa: F401
from app.database.base import Base
from app.database.database import engine

logger = get_logger(__name__)


async def on_startup(app: FastAPI) -> None:
    settings = get_settings()
    logger.info("Starting %s in %s mode", settings.APP_NAME, settings.ENVIRONMENT)

    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database schema is ready")
    except Exception:  # noqa: BLE001 - keep the app up so health checks still work
        logger.exception("Could not initialize the database schema on startup")
