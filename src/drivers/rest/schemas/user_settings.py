from datetime import datetime, time
from typing import Any
from uuid import UUID
from pydantic import BaseModel, ConfigDict, field_validator

from src.domain.value_objects.telegram_id import TelegramId


class UserSettingsBase(BaseModel):
    quiet_start_time: time | None = None
    quiet_end_time: time | None = None
    muted_days: list[str] = []
    do_not_disturb: bool = False


class UserSettingsCreate(UserSettingsBase):
    user_tg_id: int


class UserSettingsUpdate(BaseModel):
    quiet_start_time: time | None = None
    quiet_end_time: time | None = None
    muted_days: list[str] | None = None
    do_not_disturb: bool | None = None


class UserSettingsResponse(UserSettingsBase):
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
