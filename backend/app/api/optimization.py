from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.authentication import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.optimization import (
    OptimizationProfileCreate,
    OptimizationProfileRead,
    OptimizationProfileUpdate,
)
from app.services import optimization_service

router = APIRouter(prefix="/optimization", tags=["optimization"])


@router.get("", response_model=list[OptimizationProfileRead])
async def list_optimizations(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[OptimizationProfileRead]:
    return await optimization_service.list_profiles(db, current_user.id)


@router.post("", response_model=OptimizationProfileRead, status_code=status.HTTP_201_CREATED)
async def create_optimization(
    payload: OptimizationProfileCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> OptimizationProfileRead:
    return await optimization_service.create_profile(db, current_user.id, payload)


@router.get("/{profile_id}", response_model=OptimizationProfileRead)
async def get_optimization(
    profile_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> OptimizationProfileRead:
    return await optimization_service.get_profile(db, current_user.id, profile_id)


@router.patch("/{profile_id}", response_model=OptimizationProfileRead)
async def update_optimization(
    profile_id: int,
    payload: OptimizationProfileUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> OptimizationProfileRead:
    return await optimization_service.update_profile(db, current_user.id, profile_id, payload)


@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_optimization(
    profile_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    await optimization_service.delete_profile(db, current_user.id, profile_id)
