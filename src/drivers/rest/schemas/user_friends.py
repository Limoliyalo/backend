from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class UserFriendBase(BaseModel):
    owner_tg_id: int = Field(..., gt=0, description="Owner Telegram ID")
    friend_tg_id: int = Field(..., gt=0, description="Friend Telegram ID")


class UserFriendCreate(BaseModel):
    owner_tg_id: int = Field(..., gt=0, description="Owner Telegram ID")
    friend_tg_id: int = Field(..., gt=0, description="Friend Telegram ID")


class UserFriendUpdate(BaseModel):
    friend_id: UUID = Field(..., description="Friend ID")
    friend_tg_id: int = Field(..., gt=0, description="Friend Telegram ID")


class UserFriendResponse(UserFriendBase):
    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_validator("owner_tg_id", "friend_tg_id", mode="before")
    @classmethod
    def validate_telegram_ids(cls, v: Any) -> int:
        """Валидатор для owner_tg_id"""
        return v


class UserFriendDelete(BaseModel):
    friend_tg_id: int = Field(..., gt=0, description="Friend Telegram ID to delete")


class UserFriendAdminDelete(BaseModel):
    owner_tg_id: int = Field(..., gt=0, description="Owner Telegram ID")
    friend_tg_id: int = Field(..., gt=0, description="Friend Telegram ID to delete")


class FriendInfoResponse(BaseModel):
    """Полная информация о друге"""

    user_tg_id: int
    character: dict | None = None
    character_items: list[dict] = Field(default_factory=list)
    character_backgrounds: list[dict] = Field(default_factory=list)
    base_activities: list[dict] = Field(default_factory=list)
    mood_history: list[dict] = Field(default_factory=list)
    transactions: list[dict] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
