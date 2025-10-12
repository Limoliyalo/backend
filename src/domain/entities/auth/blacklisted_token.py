"""Blacklisted access token domain entity."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class BlacklistedToken:
    """Blacklisted access token entity."""

    jti: UUID
    user_tg_id: int
    reason: str
    blacklisted_at: datetime
    expires_at: datetime
