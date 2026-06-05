from datetime import datetime

from pydantic import BaseModel, Field, field_validator


MAX_NOTIFICATION_INTERVAL_MINUTES = 24 * 60
MAX_NOTIFICATION_MESSAGE_LENGTH = 200


class StartNotificationRequest(BaseModel):
    notification_time: int = Field(
        ...,
        gt=0,
        le=MAX_NOTIFICATION_INTERVAL_MINUTES,
        description="Notification interval in minutes (1-1440)",
    )
    notification_message: str | None = Field(
        default=None,
        max_length=MAX_NOTIFICATION_MESSAGE_LENGTH,
        description="Optional Telegram notification text. Blank value uses default text.",
    )

    @field_validator("notification_time")
    @classmethod
    def must_be_in_supported_range(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("notification_time must be a positive integer")
        if v > MAX_NOTIFICATION_INTERVAL_MINUTES:
            raise ValueError(
                "notification_time must not exceed "
                f"{MAX_NOTIFICATION_INTERVAL_MINUTES} minutes"
            )
        return v

    @field_validator("notification_message", mode="before")
    @classmethod
    def normalize_notification_message(cls, v: str | None) -> str | None:
        if v is None:
            return None
        trimmed = str(v).strip()
        return trimmed or None


class StartNotificationResponse(BaseModel):
    user_id: int
    interval_minutes: int
    schedule_id: str
    is_active: bool
    notification_message: str | None = None
    next_run_at: datetime | None = None
    message: str = "Notifications activated successfully"


class StopNotificationResponse(BaseModel):
    user_id: int
    is_active: bool
    message: str = "Notifications deactivated successfully"


class NotificationStatusResponse(BaseModel):
    user_id: int
    is_active: bool
    interval_minutes: int | None = None
    schedule_id: str | None = None
    notification_message: str | None = None
    next_run_at: datetime | None = None
    last_sent_at: datetime | None = None
