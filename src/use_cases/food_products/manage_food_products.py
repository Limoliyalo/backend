from dataclasses import dataclass
from typing import Any, Protocol


class FoodProductSource(Protocol):
    async def get_product(self, barcode: str) -> dict[str, Any] | None: ...


@dataclass(frozen=True)
class FoodProductNutrition:
    barcode: str
    found: bool
    has_nutrition_data: bool
    product_name: str | None
    calories_100g: float
    protein_100g: float
    fat_100g: float
    carbs_100g: float


def _empty_product(barcode: str) -> FoodProductNutrition:
    return FoodProductNutrition(
        barcode=barcode,
        found=False,
        has_nutrition_data=False,
        product_name=None,
        calories_100g=0,
        protein_100g=0,
        fat_100g=0,
        carbs_100g=0,
    )


def _number_from_nutriments(
    nutriments: dict[str, Any],
    *keys: str,
) -> float:
    for key in keys:
        value = nutriments.get(key)
        if value is None:
            continue
        try:
            parsed = float(value)
        except (TypeError, ValueError):
            continue
        if parsed >= 0:
            return parsed
    return 0


def normalize_open_food_facts_product(
    barcode: str,
    payload: dict[str, Any] | None,
) -> FoodProductNutrition:
    if not payload:
        return _empty_product(barcode)

    status = payload.get("status")
    product = payload.get("product")
    if status in (0, "failure") or not isinstance(product, dict):
        return _empty_product(barcode)

    nutriments = product.get("nutriments")
    if not isinstance(nutriments, dict):
        nutriments = {}

    calories = _number_from_nutriments(
        nutriments,
        "energy-kcal_100g",
    )
    protein = _number_from_nutriments(nutriments, "proteins_100g")
    fat = _number_from_nutriments(nutriments, "fat_100g")
    carbs = _number_from_nutriments(
        nutriments,
        "carbohydrates_100g",
    )
    has_nutrition_data = any(value > 0 for value in (calories, protein, fat, carbs))
    product_name = product.get("product_name")

    return FoodProductNutrition(
        barcode=barcode,
        found=True,
        has_nutrition_data=has_nutrition_data,
        product_name=product_name.strip() if isinstance(product_name, str) else None,
        calories_100g=calories,
        protein_100g=protein,
        fat_100g=fat,
        carbs_100g=carbs,
    )


class LookupFoodProductByBarcodeUseCase:
    def __init__(self, source: FoodProductSource) -> None:
        self._source = source

    async def execute(self, barcode: str) -> FoodProductNutrition:
        try:
            payload = await self._source.get_product(barcode)
        except Exception:
            return _empty_product(barcode)

        return normalize_open_food_facts_product(barcode, payload)
