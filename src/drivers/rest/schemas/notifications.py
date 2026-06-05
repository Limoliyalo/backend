from datetime import datetime

from pydantic import BaseModel, Field, field_validator


MAX_NOTIFICATION_INTERVAL_MINUTES = 24 * 60


class StartNotificationRequest(BaseModel):
    notification_time: int = Field(
        ...,
        gt=0,
        le=MAX_NOTIFICATION_INTERVAL_MINUTES,
        description="Notification interval in minutes (1-1440)",
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


class StartNotificationResponse(BaseModel):
    user_id: int
    interval_minutes: int
    schedule_id: str
    is_active: bool
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
    last_sent_at: datetime | None = None
