from dataclasses import dataclass, field
from datetime import datetime
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
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def revoke(self) -> None:
        if not self.revoked:
            self.revoked = True
            self.touch()

    def touch(self) -> None:
        self.updated_at = datetime.utcnow()
