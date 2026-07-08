from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.history import HistoryEntry


async def record_action(
    db: AsyncSession,
    owner_id: int,
    action: str,
    *,
    resource_type: str | None = None,
    resource_id: str | int | None = None,
    detail: str | None = None,
    commit: bool = True,
) -> HistoryEntry:
    entry = HistoryEntry(
        owner_id=owner_id,
        action=action,
        resource_type=resource_type,
        resource_id=str(resource_id) if resource_id is not None else None,
        detail=detail,
    )
    db.add(entry)
    if commit:
        await db.commit()
        await db.refresh(entry)
    return entry


async def list_history(
    db: AsyncSession, owner_id: int, *, limit: int = 100, offset: int = 0
) -> list[HistoryEntry]:
    result = await db.execute(
        select(HistoryEntry)
        .where(HistoryEntry.owner_id == owner_id)
        .order_by(HistoryEntry.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return list(result.scalars().all())
