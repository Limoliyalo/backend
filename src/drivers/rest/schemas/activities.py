from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, field_validator


class ActivityTypeBase(BaseModel):
    name: str = Field(
        ..., min_length=1, max_length=100, description="Activity type name"
    )
    unit: str = Field(..., min_length=1, max_length=50, description="Activity unit")
    color: str | None = Field(None, max_length=7, description="Color in hex format")
    daily_goal_default: int = Field(ge=1, description="Daily goal must be at least 1")


class ActivityTypeCreate(ActivityTypeBase):
    pass


class ActivityTypeUpdate(BaseModel):
    name: str | None = Field(
        None, min_length=1, max_length=100, description="Activity type name"
    )
    unit: str | None = Field(
        None, min_length=1, max_length=50, description="Activity unit"
    )
    color: str | None = Field(None, max_length=7, description="Color in hex format")
    daily_goal_default: int | None = Field(
        None, ge=1, description="Daily goal must be at least 1"
    )


class ActivityTypeResponse(ActivityTypeBase):
    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DailyActivityBase(BaseModel):
    date: datetime
    value: int = Field(default=0, ge=0, description="Value must be non-negative")
    goal: int = Field(default=1, ge=1, description="Goal must be at least 1")
    notes: str | None = Field(None, max_length=255, description="Notes")


class DailyActivityCreate(DailyActivityBase):
    character_id: UUID
    activity_type_id: UUID


class DailyActivityUpdate(BaseModel):
    value: int | None = Field(None, ge=0, description="Value must be non-negative")
    goal: int | None = Field(None, ge=1, description="Goal must be at least 1")
    notes: str | None = None


class DailyActivityResponse(DailyActivityBase):
    id: UUID
    character_id: UUID
    activity_type_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DailyProgressBase(BaseModel):
    date: datetime
    experience_gained: int = Field(
        default=0, ge=0, description="Experience gained must be non-negative"
    )
    mood_average: str | None = Field(None, max_length=50, description="Mood average")
    behavior_index: int | None = Field(
        None, ge=0, description="Behavior index must be non-negative"
    )

    @field_validator("mood_average")
    @classmethod
    def validate_mood_average(cls, v: str | None) -> str | None:
        if v is not None and v not in ["neutral", "happy", "sad", "angry", "bored"]:
            raise ValueError(
                "Mood average must be one of: neutral, happy, sad, angry, bored"
            )
        return v


class DailyProgressCreate(DailyProgressBase):
    character_id: UUID


class DailyProgressUpdate(BaseModel):
    experience_gained: int | None = Field(
        None, ge=0, description="Experience gained must be non-negative"
    )
    mood_average: str | None = None
    behavior_index: int | None = None

    @field_validator("mood_average")
    @classmethod
    def validate_mood_average(cls, v: str | None) -> str | None:
        if v is not None and v not in ["neutral", "happy", "sad", "angry", "bored"]:
            raise ValueError(
                "Mood average must be one of: neutral, happy, sad, angry, bored"
            )
        return v


class DailyProgressResponse(DailyProgressBase):
    id: UUID
    character_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MoodHistoryBase(BaseModel):
    mood: str
    trigger: str | None = None

    @field_validator("mood")
    @classmethod
    def validate_mood(cls, v: str) -> str:
        if v not in ["neutral", "happy", "sad", "angry", "bored"]:
            raise ValueError("Mood must be one of: neutral, happy, sad, angry, bored")
        return v


class MoodHistoryCreate(MoodHistoryBase):
    character_id: UUID


class MoodHistoryUpdate(BaseModel):
    mood: str | None = None
    trigger: str | None = None

    @field_validator("mood")
    @classmethod
    def validate_mood(cls, v: str | None) -> str | None:
        if v is not None and v not in ["neutral", "happy", "sad", "angry", "bored"]:
            raise ValueError("Mood must be one of: neutral, happy, sad, angry, bored")
        return v


class MoodHistoryResponse(MoodHistoryBase):
    id: UUID
    character_id: UUID
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)
