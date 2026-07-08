from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.optimization import OptimizationProfile
from app.schemas.optimization import OptimizationProfileCreate, OptimizationProfileUpdate
from app.services import history_service


async def create_profile(
    db: AsyncSession, owner_id: int, payload: OptimizationProfileCreate
) -> OptimizationProfile:
    profile = OptimizationProfile(owner_id=owner_id, **payload.model_dump())
    db.add(profile)
    await db.commit()
    await db.refresh(profile)
    await history_service.record_action(
        db,
        owner_id,
        "optimization.create",
        resource_type="optimization_profile",
        resource_id=profile.id,
        detail=f"Created profile '{profile.name}'",
    )
    return profile


async def list_profiles(db: AsyncSession, owner_id: int) -> list[OptimizationProfile]:
    result = await db.execute(
        select(OptimizationProfile)
        .where(OptimizationProfile.owner_id == owner_id)
        .order_by(OptimizationProfile.created_at.desc())
    )
    return list(result.scalars().all())


async def get_profile(
    db: AsyncSession, owner_id: int, profile_id: int
) -> OptimizationProfile:
    result = await db.execute(
        select(OptimizationProfile).where(
            OptimizationProfile.id == profile_id,
            OptimizationProfile.owner_id == owner_id,
        )
    )
    profile = result.scalar_one_or_none()
    if profile is None:
        raise NotFoundError("Optimization profile not found")
    return profile


async def update_profile(
    db: AsyncSession, owner_id: int, profile_id: int, payload: OptimizationProfileUpdate
) -> OptimizationProfile:
    profile = await get_profile(db, owner_id, profile_id)
    changes = payload.model_dump(exclude_unset=True)

    # Only one profile can be active at a time per user.
    if changes.get("is_active") is True:
        await db.execute(
            update(OptimizationProfile)
            .where(OptimizationProfile.owner_id == owner_id)
            .values(is_active=False)
        )

    for field, value in changes.items():
        setattr(profile, field, value)

    await db.commit()
    await db.refresh(profile)
    await history_service.record_action(
        db,
        owner_id,
        "optimization.update",
        resource_type="optimization_profile",
        resource_id=profile_id,
    )
    return profile


async def delete_profile(db: AsyncSession, owner_id: int, profile_id: int) -> None:
    profile = await get_profile(db, owner_id, profile_id)
    await db.delete(profile)
    await db.commit()
    await history_service.record_action(
        db,
        owner_id,
        "optimization.delete",
        resource_type="optimization_profile",
        resource_id=profile_id,
    )
