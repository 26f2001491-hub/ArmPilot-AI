from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.shutdown import on_shutdown
from app.core.startup import on_startup


@asynccontextmanager
async def lifespan(app: FastAPI):
    await on_startup(app)
    yield
    await on_shutdown(app)
