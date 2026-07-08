from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from app.database.base import Base, TimestampMixin


class Report(Base, TimestampMixin):
    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    report_type: Mapped[str] = mapped_column(String(64), nullable=False, default="benchmark_summary")
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Structured payload (aggregate stats, chart data, etc.)
    data: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
