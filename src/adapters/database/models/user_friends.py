import uuid
from datetime import datetime

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column

from src.adapters.database.base import Base


class UserFriendModel(Base):
    __tablename__ = "user_friends"
    __table_args__ = (
        UniqueConstraint("owner_tg_id", "friend_tg_id", name="uq_user_friend_pair"),
        CheckConstraint("owner_tg_id <> friend_tg_id", name="ck_user_friend_self"),
        Index("idx_user_friends_owner", "owner_tg_id"),
        Index("idx_user_friends_friend", "friend_tg_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        postgresql.UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    owner_tg_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.tg_id", ondelete="CASCADE"),
        nullable=False,
    )
    friend_tg_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.tg_id", ondelete="CASCADE"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )
