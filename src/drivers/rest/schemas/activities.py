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
    activity_type_id: UUID = Field(..., description="Activity type ID")
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


class ActivityTypeDelete(BaseModel):
    activity_type_id: UUID = Field(..., description="Activity type ID to delete")


class ActivityTypeResponse(ActivityTypeBase):
    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DailyActivityBase(BaseModel):
    date: datetime
    value: int = Field(default=0, ge=0, description="Value must be non-negative")
    goal: int | None = Field(None, ge=1, description="Goal must be at least 1")
    notes: str | None = Field(None, max_length=255, description="Notes")


class DailyActivityCreate(DailyActivityBase):
    character_id: UUID
    activity_type_id: UUID


class DailyActivityUserCreate(BaseModel):
    """Схема для создания активности пользователем (без character_id)"""

    activity_type_id: UUID = Field(..., description="Activity type ID")
    date: datetime = Field(..., description="Date of activity")
    value: int = Field(default=0, ge=0, description="Value must be non-negative")
    goal: int | None = Field(None, ge=1, description="Goal must be at least 1")
    notes: str | None = Field(None, max_length=255, description="Notes")


class DailyActivityUpdate(BaseModel):
    activity_id: UUID = Field(..., description="Activity ID")
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


class DailyProgressUserCreate(BaseModel):
    """Схема для создания прогресса пользователем (без character_id)"""

    date: datetime = Field(..., description="Date of progress")
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


class DailyProgressUpdate(BaseModel):
    progress_id: UUID = Field(..., description="Progress ID")
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


class MoodHistoryUserCreate(BaseModel):
    """Схема для создания записи настроения пользователем (без character_id)"""

    mood: str = Field(..., description="Mood")
    trigger: str | None = Field(None, description="Trigger")

    @field_validator("mood")
    @classmethod
    def validate_mood(cls, v: str) -> str:
        if v not in ["neutral", "happy", "sad", "angry", "bored"]:
            raise ValueError("Mood must be one of: neutral, happy, sad, angry, bored")
        return v


class MoodHistoryUpdate(BaseModel):
    mood_history_id: UUID = Field(..., description="Mood history ID")
    mood: str | None = None
    trigger: str | None = None

    @field_validator("mood")
    @classmethod
    def validate_mood(cls, v: str | None) -> str | None:
        if v is not None and v not in ["neutral", "happy", "sad", "angry", "bored"]:
            raise ValueError("Mood must be one of: neutral, happy, sad, angry, bored")
        return v


class MoodHistoryDelete(BaseModel):
    mood_history_id: UUID = Field(..., description="Mood history ID to delete")


class MoodHistoryResponse(MoodHistoryBase):
    id: UUID
    character_id: UUID
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


class BaseCharacterActivityBase(BaseModel):
    goal: int = Field(ge=1, description="Goal must be at least 1")


class BaseCharacterActivityCreate(BaseModel):
    character_id: UUID = Field(..., description="Character ID")
    activity_type_id: UUID
    goal: int | None = Field(None, ge=1, description="Goal must be at least 1")


class BaseCharacterActivityUserCreate(BaseModel):
    """Схема для создания базовой активности пользователем (без character_id)"""

    activity_type_id: UUID = Field(..., description="Activity type ID")
    goal: int | None = Field(None, ge=1, description="Goal must be at least 1")


class BaseCharacterActivityUpdate(BaseModel):
    activity_id: UUID = Field(..., description="Base character activity ID")
    goal: int | None = Field(None, ge=1, description="Goal must be at least 1")


class DailyActivityDelete(BaseModel):
    activity_id: UUID = Field(..., description="Activity ID to delete")


class DailyProgressDelete(BaseModel):
    progress_id: UUID = Field(..., description="Progress ID to delete")


class BaseCharacterActivityDelete(BaseModel):
    activity_id: UUID = Field(..., description="Base character activity ID to delete")


class BaseCharacterActivityResponse(BaseCharacterActivityBase):
    id: UUID
    character_id: UUID
    activity_type_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
