from datetime import datetime
from typing import Any
from uuid import UUID
from pydantic import BaseModel, ConfigDict, field_validator

from src.domain.value_objects.telegram_id import TelegramId


class CharacterBase(BaseModel):
    name: str | None = None
    sex: str | None = None
    current_mood: str = "neutral"
    level: int = 1
    total_experience: int = 0


class CharacterCreate(CharacterBase):
    user_tg_id: int


class CharacterUpdate(BaseModel):
    name: str | None = None
    sex: str | None = None
    current_mood: str | None = None


class CharacterResponse(CharacterBase):
    id: UUID
    user_tg_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_validator("user_tg_id", mode="before")
    @classmethod
    def validate_user_tg_id(cls, v: Any) -> int:
        """Преобразует TelegramId value object в int перед валидацией"""
        if isinstance(v, TelegramId):
            return v.value
        return v
