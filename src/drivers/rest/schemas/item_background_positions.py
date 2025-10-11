from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ItemBackgroundPositionBase(BaseModel):
    item_id: UUID
    background_id: UUID
    position_x: float
    position_y: float
    position_z: float = 0.0


class ItemBackgroundPositionCreate(ItemBackgroundPositionBase):
    pass


class ItemBackgroundPositionUpdate(BaseModel):
    position_x: float
    position_y: float
    position_z: float = 0.0


class ItemBackgroundPositionResponse(ItemBackgroundPositionBase):
    id: UUID

    model_config = ConfigDict(from_attributes=True)
