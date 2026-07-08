from sqlalchemy.ext.asyncio import AsyncSession

from app.models.benchmark import BenchmarkRun
from app.schemas.recommendation import Recommendation, RecommendationReport
from app.services import benchmark_service

# Heuristic thresholds tuned for Arm64 CPU LLM inference.
_TTFT_WARN_MS = 800.0
_TTFT_CRIT_MS = 2000.0
_THROUGHPUT_WARN_TPS = 15.0
_THROUGHPUT_CRIT_TPS = 5.0
_CPU_HEADROOM_PERCENT = 70.0
_MEMORY_WARN_MB = 8000.0


def _analyze(run: BenchmarkRun) -> tuple[list[Recommendation], float]:
    recs: list[Recommendation] = []
    score = 100.0

    if run.ttft_ms is not None:
        if run.ttft_ms >= _TTFT_CRIT_MS:
            score -= 30
            recs.append(
                Recommendation(
                    category="latency",
                    severity="critical",
                    title="Very high time-to-first-token",
                    detail=f"TTFT is {run.ttft_ms:.0f} ms, well above the {_TTFT_CRIT_MS:.0f} ms target.",
                    suggested_action="Enable KV-cache reuse and use a lower-bit quantization (e.g. Q4_0) to cut prefill cost.",
                )
            )
        elif run.ttft_ms >= _TTFT_WARN_MS:
            score -= 12
            recs.append(
                Recommendation(
                    category="latency",
                    severity="warning",
                    title="Elevated time-to-first-token",
                    detail=f"TTFT is {run.ttft_ms:.0f} ms.",
                    suggested_action="Pin threads to performance cores and increase the prefill batch size.",
                )
            )

    if run.throughput_tps is not None:
        if run.throughput_tps <= _THROUGHPUT_CRIT_TPS:
            score -= 30
            recs.append(
                Recommendation(
                    category="throughput",
                    severity="critical",
                    title="Low generation throughput",
                    detail=f"Throughput is {run.throughput_tps:.1f} tokens/s.",
                    suggested_action="Switch to an Arm-optimized runtime (llama.cpp with NEON/SVE or ONNX Runtime) and quantize the model.",
                )
            )
        elif run.throughput_tps <= _THROUGHPUT_WARN_TPS:
            score -= 12
            recs.append(
                Recommendation(
                    category="throughput",
                    severity="warning",
                    title="Throughput below target",
                    detail=f"Throughput is {run.throughput_tps:.1f} tokens/s.",
                    suggested_action="Increase thread count up to the number of physical cores and enable KV-cache.",
                )
            )

    if run.cpu_percent is not None and run.cpu_percent < _CPU_HEADROOM_PERCENT:
        score -= 8
        recs.append(
            Recommendation(
                category="utilization",
                severity="info",
                title="CPU under-utilized",
                detail=f"Average CPU utilization was {run.cpu_percent:.0f}%.",
                suggested_action="Raise the thread count or batch size to make fuller use of available cores.",
            )
        )

    if run.memory_mb is not None and run.memory_mb > _MEMORY_WARN_MB:
        score -= 8
        recs.append(
            Recommendation(
                category="memory",
                severity="warning",
                title="High memory footprint",
                detail=f"Peak memory was {run.memory_mb:.0f} MB.",
                suggested_action="Use a more aggressive quantization or a smaller context window to reduce the KV-cache size.",
            )
        )

    if not run.quantization:
        score -= 10
        recs.append(
            Recommendation(
                category="quantization",
                severity="warning",
                title="Model is not quantized",
                detail="This run used a full-precision model.",
                suggested_action="Quantize to 4-bit (Q4_0/Q4_K_M) for a large speed and memory win on Arm CPUs.",
            )
        )

    if not recs:
        recs.append(
            Recommendation(
                category="general",
                severity="info",
                title="Configuration looks healthy",
                detail="No obvious bottlenecks were detected for this run.",
                suggested_action="Continue monitoring under production load.",
            )
        )

    return recs, max(0.0, min(100.0, round(score, 1)))


async def build_recommendation(
    db: AsyncSession, owner_id: int, benchmark_id: int
) -> RecommendationReport:
    run = await benchmark_service.get_benchmark(db, owner_id, benchmark_id)
    recs, score = _analyze(run)
    return RecommendationReport(
        benchmark_id=run.id,
        model_name=run.model_name,
        score=score,
        recommendations=recs,
    )
