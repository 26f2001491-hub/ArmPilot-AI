from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.authentication import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.history import HistoryRead
from app.services import history_service

router = APIRouter(prefix="/history", tags=["history"])


@router.get("", response_model=list[HistoryRead])
async def list_history(
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[HistoryRead]:
    return await history_service.list_history(
        db, current_user.id, limit=limit, offset=offset
    )
