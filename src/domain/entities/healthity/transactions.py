import uuid
from dataclasses import dataclass, field
from datetime import date, datetime, timezone


@dataclass
class Transaction:
    id: uuid.UUID
    user_tg_id: int
    amount: int
    balance_after: int
    type: str
    related_item_id: uuid.UUID | None = None
    related_background_id: uuid.UUID | None = None
    description: str | None = None
    reward_date: date | None = None
    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )
