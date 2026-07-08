from statistics import mean

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.benchmark import BenchmarkRun
from app.models.report import Report
from app.schemas.reports import ReportCreate
from app.services import history_service


def _summarize(runs: list[BenchmarkRun]) -> tuple[str, dict]:
    if not runs:
        return "No benchmark runs available to summarize.", {
            "run_count": 0,
            "models": [],
        }

    def _avg(values: list[float]) -> float | None:
        clean = [v for v in values if v is not None]
        return round(mean(clean), 3) if clean else None

    avg_latency = _avg([r.latency_ms for r in runs])
    avg_throughput = _avg([r.throughput_tps for r in runs])
    avg_ttft = _avg([r.ttft_ms for r in runs])

    ranked = [r for r in runs if r.throughput_tps is not None]
    best = max(ranked, key=lambda r: r.throughput_tps) if ranked else None

    data = {
        "run_count": len(runs),
        "models": sorted({r.model_name for r in runs}),
        "avg_latency_ms": avg_latency,
        "avg_throughput_tps": avg_throughput,
        "avg_ttft_ms": avg_ttft,
        "best_model": (
            {"model_name": best.model_name, "throughput_tps": best.throughput_tps}
            if best
            else None
        ),
        "runs": [
            {
                "id": r.id,
                "model_name": r.model_name,
                "runtime": r.runtime,
                "throughput_tps": r.throughput_tps,
                "latency_ms": r.latency_ms,
            }
            for r in runs
        ],
    }

    summary = (
        f"Summary of {len(runs)} benchmark run(s) across {len(data['models'])} model(s). "
        f"Average throughput {avg_throughput} tokens/s, average latency {avg_latency} ms."
    )
    return summary, data


async def create_report(db: AsyncSession, owner_id: int, payload: ReportCreate) -> Report:
    result = await db.execute(
        select(BenchmarkRun)
        .where(BenchmarkRun.owner_id == owner_id)
        .order_by(BenchmarkRun.created_at.desc())
    )
    runs = list(result.scalars().all())
    summary, data = _summarize(runs)

    report = Report(
        owner_id=owner_id,
        title=payload.title,
        report_type=payload.report_type,
        summary=summary,
        data=data,
    )
    db.add(report)
    await db.commit()
    await db.refresh(report)
    await history_service.record_action(
        db,
        owner_id,
        "report.create",
        resource_type="report",
        resource_id=report.id,
        detail=payload.title,
    )
    return report


async def list_reports(db: AsyncSession, owner_id: int) -> list[Report]:
    result = await db.execute(
        select(Report).where(Report.owner_id == owner_id).order_by(Report.created_at.desc())
    )
    return list(result.scalars().all())


async def get_report(db: AsyncSession, owner_id: int, report_id: int) -> Report:
    result = await db.execute(
        select(Report).where(Report.id == report_id, Report.owner_id == owner_id)
    )
    report = result.scalar_one_or_none()
    if report is None:
        raise NotFoundError("Report not found")
    return report


async def delete_report(db: AsyncSession, owner_id: int, report_id: int) -> None:
    report = await get_report(db, owner_id, report_id)
    await db.delete(report)
    await db.commit()
    await history_service.record_action(
        db, owner_id, "report.delete", resource_type="report", resource_id=report_id
    )
