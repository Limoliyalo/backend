from datetime import datetime, time
from typing import Any
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.domain.value_objects.telegram_id import TelegramId


class UserSettingsBase(BaseModel):
    quiet_start_time: time | None = None
    quiet_end_time: time | None = None
    muted_days: list[str] = Field(default=[], description="List of muted days")
    do_not_disturb: bool = False

    @field_validator("muted_days")
    @classmethod
    def validate_muted_days(cls, v: list[str]) -> list[str]:
        valid_days = [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ]
        for day in v:
            if day.lower() not in valid_days:
                raise ValueError(
                    f"Invalid day: {day}. Must be one of: {', '.join(valid_days)}"
                )
        return v


class UserSettingsCreate(UserSettingsBase):
    user_tg_id: int = Field(..., gt=0, description="Telegram ID must be positive")


class UserSettingsUpdate(BaseModel):
    quiet_start_time: time | None = None
    quiet_end_time: time | None = None
    muted_days: list[str] | None = None
    do_not_disturb: bool | None = None

    @field_validator("muted_days")
    @classmethod
    def validate_muted_days(cls, v: list[str] | None) -> list[str] | None:
        if v is not None:
            valid_days = [
                "monday",
                "tuesday",
                "wednesday",
                "thursday",
                "friday",
                "saturday",
                "sunday",
            ]
            for day in v:
                if day.lower() not in valid_days:
                    raise ValueError(
                        f"Invalid day: {day}. Must be one of: {', '.join(valid_days)}"
                    )
        return v


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
