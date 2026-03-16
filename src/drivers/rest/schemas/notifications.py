from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class StartNotificationRequest(BaseModel):
    user_id: int = Field(..., description="System user ID (equals Telegram chat ID)")
    notification_time: int = Field(
        ..., gt=0, description="Notification interval in minutes (must be > 0)"
    )

    @field_validator("notification_time")
    @classmethod
    def must_be_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("notification_time must be a positive integer")
        return v


class StopNotificationRequest(BaseModel):
    user_id: int = Field(..., description="System user ID")


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
