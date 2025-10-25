from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class TelegramUser:
    """Telegram user data from init data."""

    id: int
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None
    language_code: Optional[str] = None
    is_premium: Optional[bool] = None
    photo_url: Optional[str] = None


@dataclass
class TelegramChat:
    """Telegram chat data from init data."""

    id: int
    type: str
    title: Optional[str] = None
    username: Optional[str] = None
    photo_url: Optional[str] = None


@dataclass
class TelegramChatMember:
    """Telegram chat member data from init data."""

    status: str
    user: Optional[TelegramUser] = None
    is_anonymous: Optional[bool] = None
    custom_title: Optional[str] = None


@dataclass
class TelegramAuthData:
    """Parsed and validated Telegram Mini App init data."""

    user: Optional[TelegramUser] = None
    chat: Optional[TelegramChat] = None
    chat_member: Optional[TelegramChatMember] = None
    chat_type: Optional[str] = None
    auth_date: Optional[int] = None
    start_param: Optional[str] = None
    can_send_after: Optional[int] = None
    raw_data: Optional[Dict[str, Any]] = None
