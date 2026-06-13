from pydantic import BaseModel, ConfigDict


class FoodProductNutritionResponse(BaseModel):
    barcode: str
    found: bool
    has_nutrition_data: bool
    product_name: str | None
    calories_100g: float
    protein_100g: float
    fat_100g: float
    carbs_100g: float

    model_config = ConfigDict(from_attributes=True)
