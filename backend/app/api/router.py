from fastapi import APIRouter

from app.api import (
    auth,
    benchmark,
    health,
    history,
    inference,
    metrics,
    optimization,
    recommendation,
    reports,
    settings,
    websocket,
)
from app.core.config import get_settings

app_settings = get_settings()

api_router = APIRouter()
api_router.include_router(health.router)

v1_router = APIRouter(prefix=app_settings.API_V1_PREFIX)
v1_router.include_router(auth.router)
v1_router.include_router(benchmark.router)
v1_router.include_router(history.router)
v1_router.include_router(inference.router)
v1_router.include_router(metrics.router)
v1_router.include_router(optimization.router)
v1_router.include_router(recommendation.router)
v1_router.include_router(reports.router)
v1_router.include_router(settings.router)
v1_router.include_router(websocket.router)

api_router.include_router(v1_router)
