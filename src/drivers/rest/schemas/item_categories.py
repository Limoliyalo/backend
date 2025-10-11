from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ItemCategoryBase(BaseModel):
    name: str = Field(..., max_length=100)


class ItemCategoryCreate(ItemCategoryBase):
    pass


class ItemCategoryUpdate(ItemCategoryBase):
    pass


class ItemCategoryResponse(ItemCategoryBase):
    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
