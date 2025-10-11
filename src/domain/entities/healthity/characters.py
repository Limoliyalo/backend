import uuid
from dataclasses import dataclass, field
from datetime import datetime

from src.domain.value_objects.telegram_id import TelegramId


@dataclass
class Character:
    id: uuid.UUID
    user_tg_id: TelegramId
    name: str | None = None
    sex: str | None = None
    current_mood: str = "neutral"
    level: int = 1
    total_experience: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def set_mood(self, mood: str) -> None:
        self.current_mood = mood
        self.touch()

    def add_experience(self, amount: int) -> None:
        if amount < 0:
            raise ValueError("Experience amount must be non-negative")
        self.total_experience += amount
        self._recalculate_level()
        self.touch()

    def _recalculate_level(self) -> None:
        expected_level = max(1, self.total_experience // 100)
        if expected_level != self.level:
            self.level = expected_level

    def touch(self) -> None:
        self.updated_at = datetime.utcnow()


@dataclass
class CharacterItem:
    id: uuid.UUID
    character_id: uuid.UUID
    item_id: uuid.UUID
    is_active: bool = False
    is_favourite: bool = False
    purchased_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class CharacterBackground:
    id: uuid.UUID
    character_id: uuid.UUID
    background_id: uuid.UUID
    is_active: bool = False
    is_favourite: bool = False
    purchased_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ItemBackgroundPosition:
    id: uuid.UUID
    item_id: uuid.UUID
    background_id: uuid.UUID
    position_x: float
    position_y: float
    position_z: float = 0.0
