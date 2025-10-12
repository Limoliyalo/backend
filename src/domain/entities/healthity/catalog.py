import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class ItemCategory:
    id: uuid.UUID
    name: str
    description: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class Item:
    id: uuid.UUID
    category_id: uuid.UUID
    name: str
    description: str | None = None
    cost: int = 0
    required_level: int = 1
    is_available: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def set_availability(self, available: bool) -> None:
        self.is_available = available
        self.touch()

    def touch(self) -> None:
        self.updated_at = datetime.now(timezone.utc)


@dataclass
class Background:
    id: uuid.UUID
    name: str
    description: str | None = None
    color: str | None = None
    cost: int = 0
    required_level: int = 1
    is_available: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
