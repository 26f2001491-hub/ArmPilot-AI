from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.authentication import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.settings import SettingRead, SettingUpsert
from app.services import settings_service

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("", response_model=list[SettingRead])
async def list_settings(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[SettingRead]:
    return await settings_service.list_settings(db, current_user.id)


@router.put("", response_model=SettingRead)
async def upsert_setting(
    payload: SettingUpsert,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SettingRead:
    return await settings_service.upsert_setting(db, current_user.id, payload)


@router.delete("/{key}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_setting(
    key: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    await settings_service.delete_setting(db, current_user.id, key)
