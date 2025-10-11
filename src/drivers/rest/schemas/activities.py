from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict


# Activity Type Schemas
class ActivityTypeBase(BaseModel):
    name: str
    unit: str
    color: str | None = None
    daily_goal_default: int


class ActivityTypeCreate(ActivityTypeBase):
    pass


class ActivityTypeResponse(ActivityTypeBase):
    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Daily Activity Schemas
class DailyActivityBase(BaseModel):
    date: datetime
    value: int = 0
    goal: int = 1
    notes: str | None = None


class DailyActivityCreate(DailyActivityBase):
    character_id: UUID
    activity_type_id: UUID


class DailyActivityUpdate(BaseModel):
    value: int | None = None
    goal: int | None = None
    notes: str | None = None


class DailyActivityResponse(DailyActivityBase):
    id: UUID
    character_id: UUID
    activity_type_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Daily Progress Schemas
class DailyProgressBase(BaseModel):
    date: datetime
    experience_gained: int = 0
    level_at_end: int = 1
    mood_average: str | None = None
    behavior_index: int | None = None


class DailyProgressCreate(DailyProgressBase):
    character_id: UUID


class DailyProgressUpdate(BaseModel):
    experience_gained: int | None = None
    level_at_end: int | None = None
    mood_average: str | None = None
    behavior_index: int | None = None


class DailyProgressResponse(DailyProgressBase):
    id: UUID
    character_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Mood History Schemas
class MoodHistoryBase(BaseModel):
    mood: str
    trigger: str | None = None


class MoodHistoryCreate(MoodHistoryBase):
    character_id: UUID


class MoodHistoryResponse(MoodHistoryBase):
    id: UUID
    character_id: UUID
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)
