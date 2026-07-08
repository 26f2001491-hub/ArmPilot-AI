from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.authentication import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.inference import InferenceCreate, InferenceRead
from app.services import inference_service

router = APIRouter(prefix="/inference", tags=["inference"])


@router.get("", response_model=list[InferenceRead])
async def list_inference_jobs(
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[InferenceRead]:
    return await inference_service.list_jobs(db, current_user.id, limit=limit, offset=offset)


@router.post("", response_model=InferenceRead, status_code=status.HTTP_201_CREATED)
async def create_inference_job(
    payload: InferenceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> InferenceRead:
    return await inference_service.create_job(db, current_user.id, payload)


@router.get("/{job_id}", response_model=InferenceRead)
async def get_inference_job(
    job_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> InferenceRead:
    return await inference_service.get_job(db, current_user.id, job_id)


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_inference_job(
    job_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    await inference_service.delete_job(db, current_user.id, job_id)
