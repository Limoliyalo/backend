from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from src.container import ApplicationContainer
from src.core.auth.dependencies import get_telegram_current_user
from src.drivers.rest.schemas.food_products import FoodProductNutritionResponse
from src.use_cases.food_products.manage_food_products import (
    LookupFoodProductByBarcodeUseCase,
)


router = APIRouter(prefix="/food-products", tags=["Food Products"])


@router.get("/barcode/{barcode}", response_model=FoodProductNutritionResponse)
@inject
async def lookup_food_product_by_barcode(
    barcode: str,
    telegram_id: int = Depends(get_telegram_current_user),
    use_case: LookupFoodProductByBarcodeUseCase = Depends(
        Provide[ApplicationContainer.lookup_food_product_by_barcode_use_case]
    ),
):
    _ = telegram_id
    result = await use_case.execute(barcode)
    return FoodProductNutritionResponse.model_validate(result)
