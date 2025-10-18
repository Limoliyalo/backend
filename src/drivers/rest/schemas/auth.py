from datetime import datetime

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    user_tg_id: int = Field(..., gt=0, description="Telegram ID пользователя")
    password: str = Field(..., min_length=1, description="Пароль пользователя")


class RefreshRequest(BaseModel):
    refresh_token: str = Field(..., min_length=1, description="Refresh token")


class LogoutRequest(BaseModel):
    refresh_token: str = Field(..., min_length=1, description="Refresh token")
    access_token: str | None = Field(
        None,
        description="Access token для добавления в blacklist (опционально)",
    )
    revoke_all: bool = Field(
        False,
        description="Если True, ревокировать все refresh токены пользователя",
    )


class AuthTokensResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int = Field(..., description="Срок жизни access токена в секундах")
    refresh_expires_in: int = Field(
        ..., description="Срок жизни refresh токена в секундах"
    )
    access_token_expires_at: datetime
    refresh_token_expires_at: datetime
