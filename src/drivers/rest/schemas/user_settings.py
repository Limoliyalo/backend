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
    quiet_start_time: time | None = Field(
        default=None,
        description="Время начала тихого режима. null = сбросить, не передавать = не изменять",
    )
    quiet_end_time: time | None = Field(
        default=None,
        description="Время окончания тихого режима. null = сбросить, не передавать = не изменять",
    )
    muted_days: list[str] | None = Field(
        default=None,
        description="Дни для отключения уведомлений. null = сбросить, не передавать = не изменять",
    )
    do_not_disturb: bool | None = Field(
        default=None,
        description="Режим 'Не беспокоить'. null = сбросить, не передавать = не изменять",
    )

    def to_patch_input(self, user_tg_id: int):
        """Преобразует в PatchUserSettingsInput с флагами переданных полей"""
        from src.use_cases.user_settings.manage_settings import PatchUserSettingsInput

        # Определяем, какие поля были переданы в JSON
        provided_fields = set()
        if hasattr(self, "__fields_set__"):
            provided_fields = self.__fields_set__

        return PatchUserSettingsInput(
            user_tg_id=user_tg_id,
            quiet_start_time=self.quiet_start_time,
            quiet_end_time=self.quiet_end_time,
            muted_days=self.muted_days,
            do_not_disturb=self.do_not_disturb,
            _quiet_start_time_provided="quiet_start_time" in provided_fields,
            _quiet_end_time_provided="quiet_end_time" in provided_fields,
            _muted_days_provided="muted_days" in provided_fields,
            _do_not_disturb_provided="do_not_disturb" in provided_fields,
        )

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


class MutedDaysUpdate(BaseModel):
    muted_days: list[str] = Field(..., description="List of muted days")

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


class DoNotDisturbUpdate(BaseModel):
    do_not_disturb: bool = Field(..., description="Do not disturb setting")
