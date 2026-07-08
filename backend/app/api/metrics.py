from fastapi import APIRouter, Depends

from app.auth.authentication import get_current_user
from app.models.user import User
from app.schemas.metrics import SystemMetrics
from app.services import metrics_service

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("", response_model=SystemMetrics)
async def get_metrics(
    current_user: User = Depends(get_current_user),
) -> SystemMetrics:
    return metrics_service.collect_system_metrics()
