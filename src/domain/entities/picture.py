from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional, TYPE_CHECKING

from src.domain.exceptions import InsufficientCoinsException, InsufficientLevelException
from src.domain.value_objects.telegram_id import TelegramId

if TYPE_CHECKING:  # pragma: no cover - to avoid circular imports at runtime
    from src.domain.entities.user import User


@dataclass
class Picture:
    id: int
    telegram_id: TelegramId
    level_to_open: int
    price: int
    is_opened: bool = False
    opened_at: Optional[datetime] = None

    def open(self, user: "User") -> None:
        if self.is_opened:
            return

        if user.level < self.level_to_open:
            raise InsufficientLevelException(self.level_to_open, user.level)

        if user.coins.amount < self.price:
            raise InsufficientCoinsException(self.price, user.coins.amount)

        user.spend_coins(amount=self.price)
        self.is_opened = True
        self.opened_at = datetime.now(timezone.utc)

    def can_be_opened_by(self, user: "User") -> bool:
        return (
            not self.is_opened
            and user.level >= self.level_to_open
            and user.coins.amount >= self.price
        )
