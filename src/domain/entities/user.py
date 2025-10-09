from dataclasses import dataclass, field
from datetime import datetime, timezone

from src.domain.exceptions import (
    CoinAddException,
    ExperienceAddException,
    InsufficientCoinsException,
    SpendCoinException,
)
from src.domain.value_objects.telegram_id import TelegramId
from src.domain.value_objects.coin import Coin
from src.domain.value_objects.experience import Experience


@dataclass
class User:
    telegram_id: TelegramId
    username: str
    time_to_send_message: int
    experience: Experience
    coins: Coin
    level: int = 0
    messages_count: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def as_json(self) -> dict:
        return {
            "telegram_id": self.telegram_id.value,
            "username": self.username,
            "time_to_send": self.time_to_send_message,
            "experience": self.experience.points,
            "coins": self.coins.amount,
            "level": self.level,
            "messages_count": self.messages_count,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    def add_experience(self, amount: int) -> None:
        if amount < 0:
            raise ExperienceAddException(
                message="Experience amount must be positive", experience_amount=amount
            )
        self.experience = self.experience.add(amount)
        self._check_level_up()

    def add_coins(self, amount: int) -> None:
        if amount < 0:
            raise CoinAddException("Cannot add negative coins", coins_amount=amount)
        self.coins = self.coins.add(amount)
        self.updated_at = datetime.now(timezone.utc)

    def spend_coins(self, amount: int) -> None:
        if amount < 0:
            raise SpendCoinException(message="Spend amount must be positive")
        if amount > self.coins.amount:
            raise InsufficientCoinsException(
                required=amount, available=self.coins.amount
            )
        self.coins = self.coins.subtract(amount)
        self.updated_at = datetime.now(timezone.utc)

    def increment_message_count(self) -> None:
        self.messages_count += 1

    def _check_level_up(self) -> None:
        expected_level = self.experience.points // 100
        if expected_level > self.level:
            self.level = expected_level
