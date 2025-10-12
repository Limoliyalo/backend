"""SQLAlchemy model for blacklisted access tokens."""

from datetime import datetime
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy import DateTime, Index, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.adapters.database.base import Base


class BlacklistedTokenModel(Base):
    """Blacklisted access token model."""

    __tablename__ = "blacklisted_tokens"

    jti: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        comment="JWT ID (jti) of the blacklisted token",
    )
    user_tg_id: Mapped[int] = mapped_column(
        sa.BigInteger(),
        comment="Telegram ID of the user who owned the token",
    )
    reason: Mapped[str] = mapped_column(
        String(50),
        default="logout",
        comment="Reason for blacklisting (logout, revoke_all, etc.)",
    )
    blacklisted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        comment="When the token was blacklisted",
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        comment="When the token would have expired (for cleanup)",
    )

    __table_args__ = (
        Index("ix_blacklisted_tokens_user_tg_id", "user_tg_id"),
        Index("ix_blacklisted_tokens_expires_at", "expires_at"),
    )
