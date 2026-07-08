from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base, TimestampMixin


class OptimizationProfile(Base, TimestampMixin):
    __tablename__ = "optimization_profiles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    thread_count: Mapped[int] = mapped_column(Integer, nullable=False, default=4)
    batch_size: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    quantization: Mapped[str | None] = mapped_column(String(64), nullable=True)
    kv_cache_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    cpu_affinity: Mapped[str | None] = mapped_column(String(255), nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
