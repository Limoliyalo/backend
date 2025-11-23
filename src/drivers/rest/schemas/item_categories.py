from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ItemCategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Category name")


class ItemCategoryCreate(ItemCategoryBase):
    pass


class ItemCategoryUpdate(ItemCategoryBase):
    category_id: UUID = Field(..., description="Category ID")


class ItemCategoryDelete(BaseModel):
    category_id: UUID = Field(..., description="Category ID to delete")


class ItemCategoryResponse(ItemCategoryBase):
    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
