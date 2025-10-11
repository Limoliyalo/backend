import uuid
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ItemCategory:
    id: uuid.UUID
    name: str
    description: str | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Item:
    id: uuid.UUID
    category_id: uuid.UUID
    name: str
    description: str | None = None
    cost: int = 0
    required_level: int = 1
    is_available: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def set_availability(self, available: bool) -> None:
        self.is_available = available
        self.touch()

    def touch(self) -> None:
        self.updated_at = datetime.utcnow()


@dataclass
class Background:
    id: uuid.UUID
    name: str
    description: str | None = None
    cost: int = 0
    required_level: int = 1
    is_available: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
