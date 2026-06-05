import uuid
from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column

from src.adapters.database.base import Base, TimestampMixin


class ActivityTypeModel(Base):
    __tablename__ = "activity_types"
    __table_args__ = (UniqueConstraint("name", name="uq_activity_types_name"),)

    id: Mapped[uuid.UUID] = mapped_column(
        postgresql.UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    unit: Mapped[str] = mapped_column(String(20), nullable=False)
    color: Mapped[str | None] = mapped_column(String(7), nullable=True)
    daily_goal_default: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )


class BaseCharacterActivityModel(TimestampMixin, Base):
    __tablename__ = "base_character_activities"
    __table_args__ = (
        UniqueConstraint(
            "character_id", "activity_type_id", name="uq_base_character_activity"
        ),
        Index("idx_base_character_activities_character", "character_id"),
        Index("idx_base_character_activities_type", "activity_type_id"),
        CheckConstraint("goal > 0", name="ck_base_character_activities_goal_positive"),
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
    activity_type_id: Mapped[uuid.UUID] = mapped_column(
        postgresql.UUID(as_uuid=True),
        ForeignKey("activity_types.id", ondelete="CASCADE"),
        nullable=False,
    )
    goal: Mapped[int] = mapped_column(Integer, nullable=False)


class CharacterActivityHistoryModel(TimestampMixin, Base):
    __tablename__ = "character_activity_history"
    __table_args__ = (
        UniqueConstraint(
            "character_id",
            "activity_type_id",
            "date",
            name="uq_character_activity_history",
        ),
        Index("idx_character_activity_history_character_date", "character_id", "date"),
        Index("idx_character_activity_history_type", "activity_type_id"),
        Index("idx_character_activity_history_date", "date"),
        CheckConstraint(
            "value >= 0", name="ck_character_activity_history_value_non_negative"
        ),
        CheckConstraint("goal > 0", name="ck_character_activity_history_goal_positive"),
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
    activity_type_id: Mapped[uuid.UUID] = mapped_column(
        postgresql.UUID(as_uuid=True),
        ForeignKey("activity_types.id", ondelete="CASCADE"),
        nullable=False,
    )
    date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    value: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("0"),
    )
    goal: Mapped[int] = mapped_column(Integer, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)


class FoodEntryModel(TimestampMixin, Base):
    __tablename__ = "food_entries"
    __table_args__ = (
        Index("idx_food_entries_character_consumed_at", "character_id", "consumed_at"),
        CheckConstraint("calories > 0", name="ck_food_entries_calories_positive"),
        CheckConstraint(
            "protein_g >= 0 OR protein_g IS NULL",
            name="ck_food_entries_protein_non_negative",
        ),
        CheckConstraint(
            "fat_g >= 0 OR fat_g IS NULL",
            name="ck_food_entries_fat_non_negative",
        ),
        CheckConstraint(
            "carbs_g >= 0 OR carbs_g IS NULL",
            name="ck_food_entries_carbs_non_negative",
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
    consumed_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    meal_type: Mapped[str] = mapped_column(String(20), nullable=False)
    title: Mapped[str | None] = mapped_column(String(100), nullable=True)
    calories: Mapped[int] = mapped_column(Integer, nullable=False)
    protein_g: Mapped[int | None] = mapped_column(Integer, nullable=True)
    fat_g: Mapped[int | None] = mapped_column(Integer, nullable=True)
    carbs_g: Mapped[int | None] = mapped_column(Integer, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)


class DailyProgressModel(TimestampMixin, Base):
    __tablename__ = "daily_progress"
    __table_args__ = (
        UniqueConstraint("character_id", "date", name="uq_daily_progress"),
        Index("idx_daily_progress_character_date", "character_id", "date"),
        Index("idx_daily_progress_date", "date"),
        CheckConstraint(
            "experience_gained >= 0", name="ck_daily_progress_experience_non_negative"
        ),
        CheckConstraint("level_at_end >= 1", name="ck_daily_progress_level_positive"),
        CheckConstraint(
            "behavior_index BETWEEN 0 AND 100 OR behavior_index IS NULL",
            name="ck_daily_progress_behavior_index_range",
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
    date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    experience_gained: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("0"),
    )
    level_at_end: Mapped[int] = mapped_column(Integer, nullable=False)
    mood_average: Mapped[str | None] = mapped_column(String(50), nullable=True)
    behavior_index: Mapped[int | None] = mapped_column(Integer, nullable=True)


class MoodHistoryModel(Base):
    __tablename__ = "mood_history"
    __table_args__ = (
        Index("idx_mood_history_character_time", "character_id", "timestamp"),
        Index("idx_mood_history_timestamp", "timestamp"),
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
    mood: Mapped[str] = mapped_column(String(50), nullable=False)
    trigger: Mapped[str | None] = mapped_column(Text, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )
