import uuid
from dataclasses import dataclass

from src.domain.entities.healthity.catalog import ItemCategory
from src.domain.exceptions import EntityNotFoundException
from src.ports.repositories.healthity.catalog import ItemCategoriesRepository


@dataclass
class CreateItemCategoryInput:
    name: str


@dataclass
class UpdateItemCategoryInput:
    category_id: uuid.UUID
    name: str


class ListItemCategoriesUseCase:
    def __init__(self, item_categories_repository: ItemCategoriesRepository) -> None:
        self._item_categories_repository = item_categories_repository

    async def execute(self) -> list[ItemCategory]:
        return await self._item_categories_repository.list_all()


class GetItemCategoryUseCase:
    def __init__(self, item_categories_repository: ItemCategoriesRepository) -> None:
        self._item_categories_repository = item_categories_repository

    async def execute(self, category_id: uuid.UUID) -> ItemCategory:
        category = await self._item_categories_repository.get_by_id(category_id)
        if category is None:
            raise EntityNotFoundException(f"ItemCategory {category_id} not found")
        return category


class CreateItemCategoryUseCase:
    def __init__(self, item_categories_repository: ItemCategoriesRepository) -> None:
        self._item_categories_repository = item_categories_repository

    async def execute(self, data: CreateItemCategoryInput) -> ItemCategory:
        category = ItemCategory(
            id=uuid.uuid4(),
            name=data.name,
        )
        return await self._item_categories_repository.add(category)


class UpdateItemCategoryUseCase:
    def __init__(self, item_categories_repository: ItemCategoriesRepository) -> None:
        self._item_categories_repository = item_categories_repository

    async def execute(self, data: UpdateItemCategoryInput) -> ItemCategory:
        category = await self._item_categories_repository.get_by_id(data.category_id)
        if category is None:
            raise EntityNotFoundException(f"ItemCategory {data.category_id} not found")

        category.name = data.name
        category.touch()
        return await self._item_categories_repository.update(category)


class DeleteItemCategoryUseCase:
    def __init__(self, item_categories_repository: ItemCategoriesRepository) -> None:
        self._item_categories_repository = item_categories_repository

    async def execute(self, category_id: uuid.UUID) -> None:
        category = await self._item_categories_repository.get_by_id(category_id)
        if category is None:
            raise EntityNotFoundException(f"ItemCategory {category_id} not found")
        await self._item_categories_repository.delete(category_id)
