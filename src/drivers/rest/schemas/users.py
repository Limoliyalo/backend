from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class UserBase(BaseModel):
    telegram_id: int = Field(..., gt=0, description="Telegram ID пользователя")
    is_active: bool = True
    balance: int = Field(0, ge=0, description="Баланс пользователя")


class UserCreate(UserBase):
    password: str | None = Field(
        None, description="Пароль (будет автоматически захэширован)"
    )


class UserRegister(BaseModel):
    """Публичная регистрация - только telegram_id и пароль"""

    telegram_id: int = Field(..., gt=0, description="Telegram ID пользователя")
    password: str | None = Field(
        None, description="Пароль (минимум 6 символов, опционально)"
    )

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str | None) -> str | None:
        """Валидация пароля: если передан, должен быть минимум 6 символов"""
        if v is not None and len(v) < 6:
            raise ValueError("Пароль должен содержать минимум 6 символов")
        return v


class UserUpdate(BaseModel):
    telegram_id: int = Field(..., gt=0, description="Telegram ID")
    password: str | None = Field(
        None, description="Новый пароль (будет автоматически захэширован)"
    )
    is_active: bool | None = None
    balance: int | None = Field(None, ge=0, description="Баланс пользователя")


class UserResponse(UserBase):
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DepositRequest(BaseModel):
    amount: int = Field(..., gt=0, description="Сумма пополнения")


class WithdrawRequest(BaseModel):
    amount: int = Field(..., gt=0, description="Сумма списания")


class BalanceResponse(BaseModel):
    telegram_id: int
    balance: int
    updated_at: datetime


class ChangePasswordRequest(BaseModel):
    old_password: str = Field(..., min_length=1, description="Старый пароль")
    new_password: str = Field(
        ..., min_length=6, description="Новый пароль (минимум 6 символов)"
    )


class UserDelete(BaseModel):
    telegram_id: int = Field(..., gt=0, description="Telegram ID to delete")


class UserStatisticsResponse(BaseModel):
    """Статистика пользователя"""

    user_id: int
    balance: int
    level: int | None = None
    total_experience: int | None = None
    character_name: str | None = None
    character_sex: str | None = None
    purchased_items_count: int
    purchased_backgrounds_count: int
    mood_entries_count: int
    activities_count: int
    total_transactions: int
    friends_count: int

    model_config = ConfigDict(from_attributes=True)
