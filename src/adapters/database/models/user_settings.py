import uuid

from sqlalchemy import Boolean, ForeignKey, Index, Text, Time, text
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column

from src.adapters.database.base import Base, TimestampMixin


class UserSettingsModel(TimestampMixin, Base):
    __tablename__ = "user_settings"
    __table_args__ = (Index("idx_user_settings_user", "user_tg_id"),)

    id: Mapped[uuid.UUID] = mapped_column(
        postgresql.UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_tg_id: Mapped[int] = mapped_column(
        ForeignKey("users.tg_id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    quiet_start_time: Mapped[Time | None] = mapped_column(Time, nullable=True)
    quiet_end_time: Mapped[Time | None] = mapped_column(Time, nullable=True)
    muted_days: Mapped[list[str]] = mapped_column(
        postgresql.ARRAY(Text),
        nullable=False,
        server_default=text("'{}'::text[]"),
    )
    do_not_disturb: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("false"),
    )
