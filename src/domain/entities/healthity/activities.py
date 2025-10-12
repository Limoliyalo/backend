import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class ActivityType:
    id: uuid.UUID
    name: str
    unit: str
    color: str | None
    daily_goal_default: int
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class DailyActivity:
    id: uuid.UUID
    character_id: uuid.UUID
    activity_type_id: uuid.UUID
    date: datetime
    value: int = 0
    goal: int = 1
    notes: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def touch(self) -> None:
        self.updated_at = datetime.now(timezone.utc)


@dataclass
class DailyProgress:
    id: uuid.UUID
    character_id: uuid.UUID
    date: datetime
    experience_gained: int = 0
    level_at_end: int = 1
    mood_average: str | None = None
    behavior_index: int | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def touch(self) -> None:
        self.updated_at = datetime.now(timezone.utc)


@dataclass
class MoodHistory:
    id: uuid.UUID
    character_id: uuid.UUID
    mood: str
    trigger: str | None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
