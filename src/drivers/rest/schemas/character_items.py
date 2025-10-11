from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CharacterItemBase(BaseModel):
    character_id: UUID
    item_id: UUID
    is_equipped: bool


class CharacterItemPurchase(BaseModel):
    character_id: UUID
    item_id: UUID
    is_equipped: bool = False


class CharacterItemUpdate(BaseModel):
    is_equipped: bool | None = None


class CharacterItemResponse(CharacterItemBase):
    id: UUID
    purchased_at: datetime

    model_config = ConfigDict(from_attributes=True)
