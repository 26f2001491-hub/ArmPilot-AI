from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.settings import UserSetting
from app.schemas.settings import SettingUpsert


async def list_settings(db: AsyncSession, owner_id: int) -> list[UserSetting]:
    result = await db.execute(
        select(UserSetting)
        .where(UserSetting.owner_id == owner_id)
        .order_by(UserSetting.key.asc())
    )
    return list(result.scalars().all())


async def upsert_setting(
    db: AsyncSession, owner_id: int, payload: SettingUpsert
) -> UserSetting:
    result = await db.execute(
        select(UserSetting).where(
            UserSetting.owner_id == owner_id, UserSetting.key == payload.key
        )
    )
    setting = result.scalar_one_or_none()
    if setting is None:
        setting = UserSetting(owner_id=owner_id, key=payload.key, value=payload.value)
        db.add(setting)
    else:
        setting.value = payload.value

    await db.commit()
    await db.refresh(setting)
    return setting


async def delete_setting(db: AsyncSession, owner_id: int, key: str) -> None:
    result = await db.execute(
        select(UserSetting).where(
            UserSetting.owner_id == owner_id, UserSetting.key == key
        )
    )
    setting = result.scalar_one_or_none()
    if setting is None:
        raise NotFoundError("Setting not found")
    await db.delete(setting)
    await db.commit()
