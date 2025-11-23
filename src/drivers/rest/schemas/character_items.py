from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CharacterItemBase(BaseModel):
    character_id: UUID = Field(..., description="Character ID")
    item_id: UUID = Field(..., description="Item ID")
    is_active: bool = Field(..., description="Whether item is active/equipped")
    is_favorite: bool = Field(..., description="Whether item is favorite")
    is_purchased: bool = Field(..., description="Whether item is purchased")


class CharacterItemPurchase(BaseModel):
    character_id: UUID = Field(..., description="Character ID")
    item_id: UUID = Field(..., description="Item ID")
    is_active: bool = Field(
        default=False, description="Whether item is active/equipped"
    )
    is_favorite: bool = Field(default=False, description="Whether item is favorite")
    is_purchased: bool = Field(default=False, description="Whether item is purchased")


class CharacterItemUserPurchase(BaseModel):
    item_id: UUID = Field(..., description="Item ID")


class CharacterItemUpdate(BaseModel):
    character_item_id: UUID = Field(..., description="Character item ID")
    is_active: bool | None = None
    is_favorite: bool | None = None
    is_purchased: bool | None = None


class EquipItemRequest(BaseModel):
    character_item_id: UUID = Field(..., description="Character item ID to equip")


class UnequipItemRequest(BaseModel):
    character_item_id: UUID = Field(..., description="Character item ID to unequip")


class CharacterItemDelete(BaseModel):
    character_item_id: UUID = Field(..., description="Character item ID to delete")


class CharacterItemResponse(CharacterItemBase):
    id: UUID

    model_config = ConfigDict(from_attributes=True)
