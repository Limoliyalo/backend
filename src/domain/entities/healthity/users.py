from dataclasses import dataclass, field
from datetime import datetime, time, timezone
from typing import List
import uuid

from src.domain.value_objects.telegram_id import TelegramId


@dataclass
class User:
    telegram_id: TelegramId
    password_hash: str | None = None
    is_active: bool = True
    is_admin: bool = False
    balance: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def activate(self) -> None:
        if not self.is_active:
            self.is_active = True
            self.touch()

    def deactivate(self) -> None:
        if self.is_active:
            self.is_active = False
            self.touch()

    def update_password(self, password_hash: str | None) -> None:
        self.password_hash = password_hash
        self.touch()

    def deposit(self, amount: int) -> None:
        """Пополнить баланс пользователя."""
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        self.balance += amount
        self.touch()

    def withdraw(self, amount: int) -> None:
        """Списать средства с баланса пользователя."""
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        if self.balance < amount:
            raise ValueError("Insufficient balance")
        self.balance -= amount
        self.touch()

    def touch(self) -> None:
        self.updated_at = datetime.now(timezone.utc)


@dataclass
class UserSettings:
    id: uuid.UUID
    user_tg_id: TelegramId
    quiet_start_time: time | None = None
    quiet_end_time: time | None = None
    muted_days: List[str] = field(default_factory=list)
    do_not_disturb: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def toggle_do_not_disturb(self, value: bool | None = None) -> None:
        self.do_not_disturb = not self.do_not_disturb if value is None else value
        self.touch()

    def set_quiet_time(self, start: time | None, end: time | None) -> None:
        self.quiet_start_time = start
        self.quiet_end_time = end
        self.touch()

    def set_muted_days(self, days: List[str]) -> None:
        self.muted_days = list(days)
        self.touch()

    def touch(self) -> None:
        self.updated_at = datetime.now(timezone.utc)


@dataclass
class UserFriend:
    id: uuid.UUID
    owner_tg_id: TelegramId
    friend_tg_id: TelegramId
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
