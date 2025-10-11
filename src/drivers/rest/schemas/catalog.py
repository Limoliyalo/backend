from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict


# Item Category Schemas
class ItemCategoryBase(BaseModel):
    name: str
    description: str | None = None


class ItemCategoryCreate(ItemCategoryBase):
    pass


class ItemCategoryResponse(ItemCategoryBase):
    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Item Schemas
class ItemBase(BaseModel):
    name: str
    description: str | None = None
    cost: int = 0
    required_level: int = 1
    is_available: bool = True


class ItemCreate(ItemBase):
    category_id: UUID


class ItemUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    cost: int | None = None
    required_level: int | None = None
    is_available: bool | None = None


class ItemResponse(ItemBase):
    id: UUID
    category_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Background Schemas
class BackgroundBase(BaseModel):
    name: str
    description: str | None = None
    color: str | None = None
    cost: int = 0
    required_level: int = 1
    is_available: bool = True


class BackgroundCreate(BackgroundBase):
    pass


class BackgroundUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    color: str | None = None
    cost: int | None = None
    required_level: int | None = None
    is_available: bool | None = None


class BackgroundResponse(BackgroundBase):
    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
