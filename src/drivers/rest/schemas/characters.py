from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, field_validator


class CharacterBase(BaseModel):
    name: str | None = None
    sex: str | None = None
    current_mood: str = Field(
        default="neutral",
        description="Mood must be one of: neutral, happy, sad, angry, bored",
    )
    level: int = Field(default=1, ge=1, description="Level must be at least 1")
    total_experience: int = Field(
        default=0, ge=0, description="Experience must be non-negative"
    )

    @field_validator("sex")
    @classmethod
    def validate_sex(cls, v: str | None) -> str | None:
        if v is not None and v not in ["male", "female", "other"]:
            raise ValueError("Sex must be one of: male, female, other")
        return v


class CharacterCreate(CharacterBase):
    user_tg_id: int = Field(gt=0, description="Telegram ID must be positive")


class CharacterUpdate(BaseModel):
    character_id: UUID = Field(..., description="Character ID")
    name: str | None = None
    sex: str | None = None
    current_mood: str | None = None

    @field_validator("sex")
    @classmethod
    def validate_sex(cls, v: str | None) -> str | None:
        if v is not None and v not in ["male", "female", "other"]:
            raise ValueError("Sex must be one of: male, female, other")
        return v

    @field_validator("current_mood")
    @classmethod
    def validate_mood(cls, v: str | None) -> str | None:
        if v is not None and v not in ["neutral", "happy", "sad", "angry", "bored"]:
            raise ValueError("Mood must be one of: neutral, happy, sad, angry, bored")
        return v


class CharacterUserCreate(BaseModel):
    """Схема для создания персонажа пользователем (только безопасные поля)"""

    name: str | None = None
    sex: str | None = None

    @field_validator("sex")
    @classmethod
    def validate_sex(cls, v: str | None) -> str | None:
        if v is not None and v not in ["male", "female", "other"]:
            raise ValueError("Sex must be one of: male, female, other")
        return v


class CharacterUserUpdate(BaseModel):
    """Схема для обновления персонажа пользователем (только безопасные поля)"""

    name: str | None = None
    sex: str | None = None

    @field_validator("sex")
    @classmethod
    def validate_sex(cls, v: str | None) -> str | None:
        if v is not None and v not in ["male", "female", "other"]:
            raise ValueError("Sex must be one of: male, female, other")
        return v


class CharacterDelete(BaseModel):
    character_id: UUID = Field(..., description="Character ID to delete")


class CharacterResponse(CharacterBase):
    id: UUID
    user_tg_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
