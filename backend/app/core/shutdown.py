from fastapi import FastAPI

from app.core.logger import get_logger
from app.database.database import engine

logger = get_logger(__name__)


async def on_shutdown(app: FastAPI) -> None:
    logger.info("Shutting down, disposing database engine")
    await engine.dispose()
