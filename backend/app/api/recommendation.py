from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.authentication import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.recommendation import RecommendationReport
from app.services import recommendation_service

router = APIRouter(prefix="/recommendation", tags=["recommendation"])


@router.get("/{benchmark_id}", response_model=RecommendationReport)
async def get_recommendations(
    benchmark_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RecommendationReport:
    return await recommendation_service.build_recommendation(db, current_user.id, benchmark_id)
