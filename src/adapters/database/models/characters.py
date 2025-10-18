import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column

from src.adapters.database.base import Base, TimestampMixin


class CharacterModel(TimestampMixin, Base):
    __tablename__ = "characters"
    __table_args__ = (
        UniqueConstraint("user_tg_id", name="uq_characters_user"),
        Index("idx_characters_user", "user_tg_id"),
        Index("idx_characters_level", "level"),
        CheckConstraint("level >= 1", name="ck_characters_level_positive"),
        CheckConstraint(
            "total_experience >= 0", name="ck_characters_experience_non_negative"
        ),
        CheckConstraint(
            "sex IN ('male','female','other') OR sex IS NULL",
            name="ck_characters_sex_enum",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        postgresql.UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_tg_id: Mapped[int] = mapped_column(
        ForeignKey("users.tg_id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    sex: Mapped[str | None] = mapped_column(String(20), nullable=True)
    current_mood: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        server_default=text("'neutral'"),
    )
    level: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("1"),
    )
    total_experience: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("0"),
    )


class CharacterItemModel(Base):
    __tablename__ = "character_items"
    __table_args__ = (
        UniqueConstraint("character_id", "item_id", name="uq_character_item"),
        Index("idx_character_items_character", "character_id"),
        Index(
            "idx_character_items_active",
            "character_id",
            postgresql_where=text("is_active = true"),
        ),
        Index(
            "idx_character_items_favourite",
            "character_id",
            postgresql_where=text("is_favorite = true"),
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        postgresql.UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    character_id: Mapped[uuid.UUID] = mapped_column(
        postgresql.UUID(as_uuid=True),
        ForeignKey("characters.id", ondelete="CASCADE"),
        nullable=False,
    )
    item_id: Mapped[uuid.UUID] = mapped_column(
        postgresql.UUID(as_uuid=True),
        ForeignKey("items.id", ondelete="RESTRICT"),
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("false"),
    )
    is_favorite: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("false"),
    )
    purchased_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )


class CharacterBackgroundModel(Base):
    __tablename__ = "character_backgrounds"
    __table_args__ = (
        UniqueConstraint(
            "character_id", "background_id", name="uq_character_background"
        ),
        Index("idx_character_backgrounds_character", "character_id"),
        Index(
            "idx_character_backgrounds_active",
            "character_id",
            postgresql_where=text("is_active = true"),
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        postgresql.UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    character_id: Mapped[uuid.UUID] = mapped_column(
        postgresql.UUID(as_uuid=True),
        ForeignKey("characters.id", ondelete="CASCADE"),
        nullable=False,
    )
    background_id: Mapped[uuid.UUID] = mapped_column(
        postgresql.UUID(as_uuid=True),
        ForeignKey("backgrounds.id", ondelete="RESTRICT"),
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("false"),
    )
    is_favorite: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("false"),
    )
    purchased_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )


class ItemBackgroundPositionModel(Base):
    __tablename__ = "item_background_positions"
    __table_args__ = (
        UniqueConstraint(
            "item_id", "background_id", name="uq_item_background_position"
        ),
        Index("idx_item_bg_positions_item", "item_id"),
        Index("idx_item_bg_positions_bg", "background_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        postgresql.UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    item_id: Mapped[uuid.UUID] = mapped_column(
        postgresql.UUID(as_uuid=True),
        ForeignKey("items.id", ondelete="CASCADE"),
        nullable=False,
    )
    background_id: Mapped[uuid.UUID] = mapped_column(
        postgresql.UUID(as_uuid=True),
        ForeignKey("backgrounds.id", ondelete="CASCADE"),
        nullable=False,
    )
    position_x: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    position_y: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    position_z: Mapped[float] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        server_default=text("0"),
    )
