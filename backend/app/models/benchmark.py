from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base, TimestampMixin


class BenchmarkRun(Base, TimestampMixin):
    __tablename__ = "benchmark_runs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )

    model_name: Mapped[str] = mapped_column(String(255), nullable=False)
    runtime: Mapped[str] = mapped_column(String(64), nullable=False, default="onnxruntime")
    quantization: Mapped[str | None] = mapped_column(String(64), nullable=True)
    prompt_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    generated_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Measured metrics
    latency_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    throughput_tps: Mapped[float | None] = mapped_column(Float, nullable=True)
    ttft_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    memory_mb: Mapped[float | None] = mapped_column(Float, nullable=True)
    cpu_percent: Mapped[float | None] = mapped_column(Float, nullable=True)

    status: Mapped[str] = mapped_column(String(32), nullable=False, default="completed")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
