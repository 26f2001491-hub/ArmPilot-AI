from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base, TimestampMixin


class InferenceJob(Base, TimestampMixin):
    __tablename__ = "inference_jobs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )

    model_name: Mapped[str] = mapped_column(String(255), nullable=False)
    runtime: Mapped[str] = mapped_column(String(64), nullable=False, default="onnxruntime")
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    max_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=128)

    # queued -> running -> completed / failed
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="queued", index=True)
    output: Mapped[str | None] = mapped_column(Text, nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)

    prompt_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    generated_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
