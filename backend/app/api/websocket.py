import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.auth.jwt import decode_access_token
from app.core.logger import get_logger
from app.services import metrics_service

logger = get_logger(__name__)

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/metrics")
async def metrics_stream(websocket: WebSocket) -> None:
    """Stream live system metrics.

    Authenticated with a JWT passed as the ``token`` query parameter, e.g.
    ``ws://host/ws/metrics?token=<access_token>``.
    """
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=1008)
        return

    try:
        decode_access_token(token)
    except ValueError:
        await websocket.close(code=1008)
        return

    await websocket.accept()
    try:
        while True:
            metrics = metrics_service.collect_system_metrics()
            await websocket.send_json(metrics.model_dump())
            await asyncio.sleep(1.0)
    except WebSocketDisconnect:
        logger.info("Metrics websocket client disconnected")
