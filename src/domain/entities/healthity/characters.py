import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class Character:
    id: uuid.UUID
    user_tg_id: int
    name: str | None = None
    sex: str | None = None
    current_mood: str = "neutral"
    level: int = 1
    total_experience: int = 0
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )
    updated_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )

    def set_mood(self, mood: str) -> None:
        self.current_mood = mood
        self.touch()

    def add_experience(self, amount: int) -> None:
        if amount < 0:
            raise ValueError("Experience amount must be non-negative")
        self.total_experience += amount
        self._recalculate_level()
        self.touch()

    def set_experience(self, amount: int) -> None:
        self.total_experience = max(0, amount)
        self._recalculate_level()
        self.touch()

    def _recalculate_level(self) -> None:
        expected_level = max(1, self.total_experience // 100)
        if expected_level != self.level:
            self.level = expected_level

    def touch(self) -> None:
        self.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)


@dataclass
class CharacterItem:
    id: uuid.UUID
    character_id: uuid.UUID
    item_id: uuid.UUID
    is_active: bool = False
    is_favorite: bool = False
    is_purchased: bool = False

    def equip(self) -> None:
        if not self.is_purchased:
            raise ValueError("Item must be purchased before it can be equipped")
        self.is_active = True

    def unequip(self) -> None:
        self.is_active = False

    def toggle_favorite(self) -> None:
        self.is_favorite = not self.is_favorite


@dataclass
class CharacterBackground:
    id: uuid.UUID
    character_id: uuid.UUID
    background_id: uuid.UUID
    is_active: bool = False
    is_favorite: bool = False
    is_purchased: bool = False

    def activate(self) -> None:
        if not self.is_purchased:
            raise ValueError("Background must be purchased before it can be activated")
        self.is_active = True

    def deactivate(self) -> None:
        self.is_active = False

    def toggle_favorite(self) -> None:
        self.is_favorite = not self.is_favorite


@dataclass
class ItemBackgroundPosition:
    id: uuid.UUID
    item_id: uuid.UUID
    background_id: uuid.UUID
    position_x: float
    position_y: float
    position_z: float = 0.0
    size: float = 0.0
