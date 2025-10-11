from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Index,
    Integer,
    String,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from src.adapters.database.base import Base, TimestampMixin


class UserModel(TimestampMixin, Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint("balance >= 0", name="ck_users_balance_non_negative"),
        Index("idx_users_is_active", "is_active"),
        Index("idx_users_created_at", "created_at"),
    )

    tg_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    password_hash: Mapped[str | None] = mapped_column(String(length=255), nullable=True)
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("true"),
    )
    is_admin: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("false"),
    )
    balance: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("0"),
    )
