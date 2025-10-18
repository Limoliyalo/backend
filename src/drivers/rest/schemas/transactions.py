from datetime import datetime
from typing import Any
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.domain.value_objects.telegram_id import TelegramId


class TransactionBase(BaseModel):
    amount: int = Field(..., description="Transaction amount")
    type: str
    description: str | None = None


class TransactionCreate(TransactionBase):
    user_tg_id: int = Field(..., gt=0, description="Telegram ID must be positive")
    related_item_id: UUID | None = None
    related_background_id: UUID | None = None


class TransactionUpdate(BaseModel):
    amount: int | None = None
    type: str | None = None
    description: str | None = None


class TransactionResponse(TransactionBase):
    id: UUID
    user_tg_id: int
    balance_after: int
    related_item_id: UUID | None = None
    related_background_id: UUID | None = None
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_validator("user_tg_id", mode="before")
    @classmethod
    def validate_user_tg_id(cls, v: Any) -> int:
        """Преобразует TelegramId value object в int перед валидацией"""
        if isinstance(v, TelegramId):
            return v.value
        return v
