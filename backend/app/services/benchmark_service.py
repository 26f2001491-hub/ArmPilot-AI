from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.benchmark import BenchmarkRun
from app.schemas.benchmark import BenchmarkCreate
from app.services import history_service


def _derive_metrics(payload: BenchmarkCreate) -> dict:
    """Fill in throughput from latency/tokens when it was not supplied."""
    values = payload.model_dump()
    if (
        values.get("throughput_tps") is None
        and values.get("latency_ms")
        and values.get("generated_tokens")
    ):
        seconds = values["latency_ms"] / 1000.0
        if seconds > 0:
            values["throughput_tps"] = round(values["generated_tokens"] / seconds, 3)
    return values


async def create_benchmark(
    db: AsyncSession, owner_id: int, payload: BenchmarkCreate
) -> BenchmarkRun:
    run = BenchmarkRun(owner_id=owner_id, **_derive_metrics(payload))
    db.add(run)
    await db.commit()
    await db.refresh(run)
    await history_service.record_action(
        db,
        owner_id,
        "benchmark.create",
        resource_type="benchmark",
        resource_id=run.id,
        detail=f"Benchmarked {run.model_name} on {run.runtime}",
    )
    return run


async def list_benchmarks(
    db: AsyncSession, owner_id: int, *, limit: int = 100, offset: int = 0
) -> list[BenchmarkRun]:
    result = await db.execute(
        select(BenchmarkRun)
        .where(BenchmarkRun.owner_id == owner_id)
        .order_by(BenchmarkRun.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return list(result.scalars().all())


async def get_benchmark(db: AsyncSession, owner_id: int, benchmark_id: int) -> BenchmarkRun:
    result = await db.execute(
        select(BenchmarkRun).where(
            BenchmarkRun.id == benchmark_id, BenchmarkRun.owner_id == owner_id
        )
    )
    run = result.scalar_one_or_none()
    if run is None:
        raise NotFoundError("Benchmark run not found")
    return run


async def delete_benchmark(db: AsyncSession, owner_id: int, benchmark_id: int) -> None:
    run = await get_benchmark(db, owner_id, benchmark_id)
    await db.delete(run)
    await db.commit()
    await history_service.record_action(
        db, owner_id, "benchmark.delete", resource_type="benchmark", resource_id=benchmark_id
    )
