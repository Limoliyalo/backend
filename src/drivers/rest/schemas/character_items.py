from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CharacterItemBase(BaseModel):
    character_id: UUID = Field(..., description="Character ID")
    item_id: UUID = Field(..., description="Item ID")
    is_active: bool = Field(..., description="Whether item is active/equipped")
    is_favorite: bool = Field(..., description="Whether item is favourite")


class CharacterItemPurchase(BaseModel):
    character_id: UUID = Field(..., description="Character ID")
    item_id: UUID = Field(..., description="Item ID")
    is_active: bool = Field(
        default=False, description="Whether item is active/equipped"
    )
    is_favorite: bool = Field(default=False, description="Whether item is favourite")


class CharacterItemUpdate(BaseModel):
    is_active: bool | None = None
    is_favorite: bool | None = None


class CharacterItemResponse(CharacterItemBase):
    id: UUID
    purchased_at: datetime

    model_config = ConfigDict(from_attributes=True)
