from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CharacterBackgroundBase(BaseModel):
    character_id: UUID
    background_id: UUID
    is_active: bool


class CharacterBackgroundPurchase(BaseModel):
    character_id: UUID
    background_id: UUID
    is_active: bool = False


class CharacterBackgroundUpdate(BaseModel):
    is_active: bool | None = None


class CharacterBackgroundResponse(CharacterBackgroundBase):
    id: UUID
    purchased_at: datetime

    model_config = ConfigDict(from_attributes=True)
