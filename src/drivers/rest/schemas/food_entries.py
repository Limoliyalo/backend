from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


MealType = Literal["breakfast", "lunch", "dinner", "snack", "other"]


def _trim_optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    trimmed = value.strip()
    return trimmed or None


class FoodEntryCreate(BaseModel):
    consumed_at: datetime
    meal_type: MealType = "other"
    title: str | None = Field(None, max_length=100)
    calories: int = Field(gt=0)
    protein_g: int | None = Field(None, ge=0)
    fat_g: int | None = Field(None, ge=0)
    carbs_g: int | None = Field(None, ge=0)
    notes: str | None = Field(None, max_length=255)

    @field_validator("title", "notes", mode="before")
    @classmethod
    def trim_optional_text(cls, value: str | None) -> str | None:
        return _trim_optional_text(value)


class FoodEntryUpdate(BaseModel):
    entry_id: UUID
    consumed_at: datetime | None = None
    meal_type: MealType | None = None
    title: str | None = Field(None, max_length=100)
    calories: int | None = Field(None, gt=0)
    protein_g: int | None = Field(None, ge=0)
    fat_g: int | None = Field(None, ge=0)
    carbs_g: int | None = Field(None, ge=0)
    notes: str | None = Field(None, max_length=255)

    @field_validator("title", "notes", mode="before")
    @classmethod
    def trim_optional_text(cls, value: str | None) -> str | None:
        return _trim_optional_text(value)


class FoodEntryDelete(BaseModel):
    entry_id: UUID


class FoodEntryResponse(BaseModel):
    id: UUID
    character_id: UUID
    consumed_at: datetime
    meal_type: str
    title: str | None
    calories: int
    protein_g: int | None
    fat_g: int | None
    carbs_g: int | None
    notes: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FoodEntrySummaryResponse(BaseModel):
    total_calories: int
    total_protein_g: int
    total_fat_g: int
    total_carbs_g: int
    last_entry_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class FoodEntriesDayResponse(BaseModel):
    entries: list[FoodEntryResponse]
    summary: FoodEntrySummaryResponse

    model_config = ConfigDict(from_attributes=True)
