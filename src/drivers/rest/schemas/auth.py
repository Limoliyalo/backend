from datetime import datetime
from typing import Optional

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


# Telegram Mini App schemas
class TelegramUserResponse(BaseModel):
    id: int
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None
    language_code: Optional[str] = None
    is_premium: Optional[bool] = None
    photo_url: Optional[str] = None


class TelegramChatResponse(BaseModel):
    id: int
    type: str
    title: Optional[str] = None
    username: Optional[str] = None
    photo_url: Optional[str] = None


class TelegramChatMemberResponse(BaseModel):
    status: str
    user: Optional[TelegramUserResponse] = None
    is_anonymous: Optional[bool] = None
    custom_title: Optional[str] = None


class TelegramAuthDataResponse(BaseModel):
    user: Optional[TelegramUserResponse] = None
    chat: Optional[TelegramChatResponse] = None
    chat_member: Optional[TelegramChatMemberResponse] = None
    chat_type: Optional[str] = None
    auth_date: Optional[int] = None
    start_param: Optional[str] = None
    can_send_after: Optional[int] = None
