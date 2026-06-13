import asyncio

from src.use_cases.food_products.manage_food_products import (
    LookupFoodProductByBarcodeUseCase,
)


class StaticProductSource:
    def __init__(self, payload):
        self.payload = payload
        self.calls: list[str] = []

    async def get_product(self, barcode: str):
        self.calls.append(barcode)
        return self.payload


class FailingProductSource:
    async def get_product(self, barcode: str):
        raise RuntimeError(f"Open Food Facts unavailable for {barcode}")


def test_food_product_lookup_normalizes_open_food_facts_nutrition() -> None:
    source = StaticProductSource(
        {
            "status": "success",
            "product": {
                "product_name": "Greek yogurt",
                "nutriments": {
                    "energy-kcal_100g": 63.4,
                    "proteins_100g": 4,
                    "fat_100g": 1.5,
                    "carbohydrates_100g": 10,
                },
            },
        }
    )
    use_case = LookupFoodProductByBarcodeUseCase(source)

    async def run() -> None:
        result = await use_case.execute("4601234567890")

        assert source.calls == ["4601234567890"]
        assert result.barcode == "4601234567890"
        assert result.found is True
        assert result.has_nutrition_data is True
        assert result.product_name == "Greek yogurt"
        assert result.calories_100g == 63.4
        assert result.protein_100g == 4
        assert result.fat_100g == 1.5
        assert result.carbs_100g == 10

    asyncio.run(run())


def test_food_product_lookup_returns_zeroes_when_nutrition_is_missing() -> None:
    source = StaticProductSource(
        {
            "status": "success",
            "product": {
                "product_name": "Mystery snack",
                "nutriments": {},
            },
        }
    )
    use_case = LookupFoodProductByBarcodeUseCase(source)

    async def run() -> None:
        result = await use_case.execute("0000000000000")

        assert result.found is True
        assert result.has_nutrition_data is False
        assert result.product_name == "Mystery snack"
        assert result.calories_100g == 0
        assert result.protein_100g == 0
        assert result.fat_100g == 0
        assert result.carbs_100g == 0

    asyncio.run(run())


def test_food_product_lookup_handles_missing_product_and_source_errors() -> None:
    not_found_use_case = LookupFoodProductByBarcodeUseCase(
        StaticProductSource({"status": "failure"})
    )
    failing_use_case = LookupFoodProductByBarcodeUseCase(FailingProductSource())

    async def run() -> None:
        missing = await not_found_use_case.execute("111")
        failed = await failing_use_case.execute("222")

        for result, barcode in ((missing, "111"), (failed, "222")):
            assert result.barcode == barcode
            assert result.found is False
            assert result.has_nutrition_data is False
            assert result.product_name is None
            assert result.calories_100g == 0
            assert result.protein_100g == 0
            assert result.fat_100g == 0
            assert result.carbs_100g == 0

    asyncio.run(run())
