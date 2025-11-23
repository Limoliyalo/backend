from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CharacterBackgroundBase(BaseModel):
    character_id: UUID = Field(..., description="Character ID")
    background_id: UUID = Field(..., description="Background ID")
    is_active: bool = Field(..., description="Whether background is active/equipped")
    is_favorite: bool = Field(..., description="Whether background is favorite")
    is_purchased: bool = Field(..., description="Whether background is purchased")


class CharacterBackgroundPurchase(BaseModel):
    character_id: UUID = Field(..., description="Character ID")
    background_id: UUID = Field(..., description="Background ID")
    is_active: bool = Field(
        default=False, description="Whether background is active/equipped"
    )
    is_favorite: bool = Field(
        default=False, description="Whether background is favorite"
    )
    is_purchased: bool = Field(
        default=False, description="Whether background is purchased"
    )


class CharacterBackgroundUserPurchase(BaseModel):
    background_id: UUID = Field(..., description="Background ID")


class CharacterBackgroundToggleFavorite(BaseModel):
    character_id: UUID = Field(..., description="Character ID")
    background_id: UUID = Field(..., description="Background ID")


class CharacterBackgroundUpdate(BaseModel):
    background_id: UUID = Field(..., description="Background ID")
    is_active: bool | None = None
    is_favorite: bool | None = None
    is_purchased: bool | None = None


class EquipBackgroundRequest(BaseModel):
    background_id: UUID = Field(..., description="Background ID to equip")


class UnequipBackgroundRequest(BaseModel):
    background_id: UUID = Field(..., description="Background ID to unequip")


class CharacterBackgroundDelete(BaseModel):
    background_id: UUID = Field(..., description="Background ID to delete")


class CharacterBackgroundResponse(CharacterBackgroundBase):
    id: UUID

    model_config = ConfigDict(from_attributes=True)
