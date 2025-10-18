from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ItemBackgroundPositionBase(BaseModel):
    item_id: UUID = Field(..., description="Item ID")
    background_id: UUID = Field(..., description="Background ID")
    position_x: float = Field(..., description="X position")
    position_y: float = Field(..., description="Y position")
    position_z: float = Field(default=0.0, description="Z position")


class ItemBackgroundPositionCreate(ItemBackgroundPositionBase):
    pass


class ItemBackgroundPositionUpdate(BaseModel):
    position_x: float = Field(..., description="X position")
    position_y: float = Field(..., description="Y position")
    position_z: float = Field(default=0.0, description="Z position")


class ItemBackgroundPositionResponse(ItemBackgroundPositionBase):
    id: UUID

    model_config = ConfigDict(from_attributes=True)
