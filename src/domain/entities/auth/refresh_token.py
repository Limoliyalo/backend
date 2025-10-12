from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID

from src.domain.value_objects.telegram_id import TelegramId


@dataclass
class RefreshToken:
    id: UUID
    user_tg_id: TelegramId
    token_hash: str
    jti: UUID
    expires_at: datetime
    revoked: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def revoke(self) -> None:
        if not self.revoked:
            self.revoked = True
            self.touch()

    def touch(self) -> None:
        self.updated_at = datetime.now(timezone.utc)
