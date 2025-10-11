import uuid
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ActivityType:
    id: uuid.UUID
    name: str
    unit: str
    color: str | None
    daily_goal_default: int
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class DailyActivity:
    id: uuid.UUID
    character_id: uuid.UUID
    activity_type_id: uuid.UUID
    date: datetime
    value: int = 0
    goal: int = 1
    notes: str | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def touch(self) -> None:
        self.updated_at = datetime.utcnow()


@dataclass
class DailyProgress:
    id: uuid.UUID
    character_id: uuid.UUID
    date: datetime
    experience_gained: int = 0
    level_at_end: int = 1
    mood_average: str | None = None
    behavior_index: int | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def touch(self) -> None:
        self.updated_at = datetime.utcnow()


@dataclass
class MoodHistory:
    id: uuid.UUID
    character_id: uuid.UUID
    mood: str
    trigger: str | None
    timestamp: datetime = field(default_factory=datetime.utcnow)
