from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.authentication import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.benchmark import BenchmarkCreate, BenchmarkRead
from app.services import benchmark_service

router = APIRouter(prefix="/benchmark", tags=["benchmark"])


@router.get("", response_model=list[BenchmarkRead])
async def list_benchmarks(
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[BenchmarkRead]:
    return await benchmark_service.list_benchmarks(
        db, current_user.id, limit=limit, offset=offset
    )


@router.post("", response_model=BenchmarkRead, status_code=status.HTTP_201_CREATED)
async def create_benchmark(
    payload: BenchmarkCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> BenchmarkRead:
    return await benchmark_service.create_benchmark(db, current_user.id, payload)


@router.get("/{benchmark_id}", response_model=BenchmarkRead)
async def get_benchmark(
    benchmark_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> BenchmarkRead:
    return await benchmark_service.get_benchmark(db, current_user.id, benchmark_id)


@router.delete("/{benchmark_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_benchmark(
    benchmark_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    await benchmark_service.delete_benchmark(db, current_user.id, benchmark_id)
