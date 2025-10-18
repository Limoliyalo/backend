from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.domain.value_objects.telegram_id import TelegramId


class UserFriendBase(BaseModel):
    owner_tg_id: int = Field(..., gt=0, description="Owner Telegram ID")
    friend_tg_id: int = Field(..., gt=0, description="Friend Telegram ID")


class UserFriendCreate(BaseModel):
    friend_tg_id: int = Field(..., gt=0, description="Friend Telegram ID")


class UserFriendUpdate(BaseModel):
    friend_tg_id: int = Field(..., gt=0, description="Friend Telegram ID")


class UserFriendResponse(UserFriendBase):
    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_validator("owner_tg_id", "friend_tg_id", mode="before")
    @classmethod
    def validate_telegram_ids(cls, v: Any) -> int:
        """Преобразует TelegramId value object в int перед валидацией"""
        if isinstance(v, TelegramId):
            return v.value
        return v
