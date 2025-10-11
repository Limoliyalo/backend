from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.domain.value_objects.telegram_id import TelegramId


# User schemas
class UserBase(BaseModel):
    telegram_id: int = Field(..., description="Telegram ID пользователя")
    is_active: bool = True
    balance: int = Field(0, ge=0)


class UserCreate(UserBase):
    password: str | None = Field(
        None, description="Пароль (будет автоматически захэширован)"
    )


class UserUpdate(BaseModel):
    password: str | None = Field(
        None, description="Новый пароль (будет автоматически захэширован)"
    )
    is_active: bool | None = None
    balance: int | None = Field(None, ge=0, description="Баланс пользователя")


class UserResponse(UserBase):
    password_hash: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_validator("telegram_id", mode="before")
    @classmethod
    def validate_telegram_id(cls, v: Any) -> int:
        """Преобразует TelegramId value object в int перед валидацией"""
        if isinstance(v, TelegramId):
            return v.value
        return v


class DepositRequest(BaseModel):
    amount: int = Field(..., gt=0, description="Сумма пополнения")


class WithdrawRequest(BaseModel):
    amount: int = Field(..., gt=0, description="Сумма списания")


class BalanceResponse(BaseModel):
    telegram_id: int
    balance: int
    updated_at: datetime
