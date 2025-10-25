from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CharacterBackgroundBase(BaseModel):
    character_id: UUID = Field(..., description="Character ID")
    background_id: UUID = Field(..., description="Background ID")
    is_active: bool = Field(..., description="Whether background is active/equipped")
    is_favorite: bool = Field(..., description="Whether background is favourite")


class CharacterBackgroundPurchase(BaseModel):
    character_id: UUID = Field(..., description="Character ID")
    background_id: UUID = Field(..., description="Background ID")
    is_active: bool = Field(
        default=False, description="Whether background is active/equipped"
    )
    is_favorite: bool = Field(
        default=False, description="Whether background is favourite"
    )


class CharacterBackgroundUserPurchase(BaseModel):
    background_id: UUID = Field(..., description="Background ID")


class CharacterBackgroundUpdate(BaseModel):
    is_active: bool | None = None
    is_favorite: bool | None = None


class CharacterBackgroundResponse(CharacterBackgroundBase):
    id: UUID
    purchased_at: datetime

    model_config = ConfigDict(from_attributes=True)
