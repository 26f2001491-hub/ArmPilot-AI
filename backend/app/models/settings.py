from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base, TimestampMixin


class UserSetting(Base, TimestampMixin):
    """A per-user key/value preference store."""

    __tablename__ = "user_settings"
    __table_args__ = (UniqueConstraint("owner_id", "key", name="uq_user_setting_owner_key"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )

    key: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    value: Mapped[str | None] = mapped_column(Text, nullable=True)
