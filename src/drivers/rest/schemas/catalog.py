from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class ItemCategoryBase(BaseModel):
    name: str
    description: str | None = None


class ItemCategoryCreate(ItemCategoryBase):
    pass


class ItemCategoryResponse(ItemCategoryBase):
    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ItemBase(BaseModel):
    name: str
    description: str | None = None
    cost: int = Field(ge=0, description="Cost must be non-negative")
    required_level: int = Field(ge=1, description="Required level must be at least 1")
    is_available: bool = True


class ItemCreate(ItemBase):
    category_id: UUID


class ItemUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    cost: int | None = Field(None, ge=0, description="Cost must be non-negative")
    required_level: int | None = Field(
        None, ge=1, description="Required level must be at least 1"
    )
    is_available: bool | None = None


class ItemResponse(ItemBase):
    id: UUID
    category_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BackgroundBase(BaseModel):
    name: str
    description: str | None = None
    color: str | None = None
    cost: int = Field(ge=0, description="Cost must be non-negative")
    required_level: int = Field(ge=1, description="Required level must be at least 1")
    is_available: bool = True


class BackgroundCreate(BackgroundBase):
    pass


class BackgroundUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    color: str | None = None
    cost: int | None = Field(None, ge=0, description="Cost must be non-negative")
    required_level: int | None = Field(
        None, ge=1, description="Required level must be at least 1"
    )
    is_available: bool | None = None


class BackgroundResponse(BackgroundBase):
    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
