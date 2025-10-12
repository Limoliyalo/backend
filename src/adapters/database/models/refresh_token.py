from datetime import datetime
from uuid import uuid4

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.adapters.database.base import Base, TimestampMixin


class RefreshTokenModel(TimestampMixin, Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    user_tg_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.tg_id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    token_hash: Mapped[str] = mapped_column(String(length=128), nullable=False)
    jti: Mapped[UUID] = mapped_column(UUID(as_uuid=True), nullable=False, unique=True)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    revoked: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("false"),
    )
