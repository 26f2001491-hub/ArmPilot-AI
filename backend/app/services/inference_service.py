from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.core.logger import get_logger
from app.inference.runtime import get_runtime
from app.models.inference import InferenceJob
from app.schemas.inference import InferenceCreate
from app.services import history_service

logger = get_logger(__name__)


async def _run_job(db: AsyncSession, job: InferenceJob) -> None:
    job.status = "running"
    await db.commit()
    try:
        runtime = get_runtime(job.runtime)
        result = runtime.generate(job.prompt, job.max_tokens)
        job.output = result.output
        job.prompt_tokens = result.prompt_tokens
        job.generated_tokens = result.generated_tokens
        job.latency_ms = result.latency_ms
        job.status = "completed"
    except Exception as exc:  # noqa: BLE001 - persist the failure for the client
        logger.exception("Inference job %s failed", job.id)
        job.status = "failed"
        job.error = str(exc)
    await db.commit()
    await db.refresh(job)


async def create_job(
    db: AsyncSession, owner_id: int, payload: InferenceCreate
) -> InferenceJob:
    job = InferenceJob(
        owner_id=owner_id,
        model_name=payload.model_name,
        runtime=payload.runtime,
        prompt=payload.prompt,
        max_tokens=payload.max_tokens,
        status="queued",
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)

    await _run_job(db, job)

    await history_service.record_action(
        db,
        owner_id,
        "inference.run",
        resource_type="inference_job",
        resource_id=job.id,
        detail=f"{job.model_name} via {job.runtime} ({job.status})",
    )
    return job


async def list_jobs(
    db: AsyncSession, owner_id: int, *, limit: int = 100, offset: int = 0
) -> list[InferenceJob]:
    result = await db.execute(
        select(InferenceJob)
        .where(InferenceJob.owner_id == owner_id)
        .order_by(InferenceJob.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return list(result.scalars().all())


async def get_job(db: AsyncSession, owner_id: int, job_id: int) -> InferenceJob:
    result = await db.execute(
        select(InferenceJob).where(
            InferenceJob.id == job_id, InferenceJob.owner_id == owner_id
        )
    )
    job = result.scalar_one_or_none()
    if job is None:
        raise NotFoundError("Inference job not found")
    return job


async def delete_job(db: AsyncSession, owner_id: int, job_id: int) -> None:
    job = await get_job(db, owner_id, job_id)
    await db.delete(job)
    await db.commit()
    await history_service.record_action(
        db, owner_id, "inference.delete", resource_type="inference_job", resource_id=job_id
    )
