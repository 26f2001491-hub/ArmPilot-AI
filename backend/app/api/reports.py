from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.authentication import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.reports import ReportCreate, ReportRead
from app.services import report_service

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("", response_model=list[ReportRead])
async def list_reports(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ReportRead]:
    return await report_service.list_reports(db, current_user.id)


@router.post("", response_model=ReportRead, status_code=status.HTTP_201_CREATED)
async def create_report(
    payload: ReportCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ReportRead:
    return await report_service.create_report(db, current_user.id, payload)


@router.get("/{report_id}", response_model=ReportRead)
async def get_report(
    report_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ReportRead:
    return await report_service.get_report(db, current_user.id, report_id)


@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_report(
    report_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    await report_service.delete_report(db, current_user.id, report_id)
