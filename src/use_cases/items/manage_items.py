import uuid
from dataclasses import dataclass

from src.domain.entities.healthity.catalog import Item
from src.domain.exceptions import EntityNotFoundException
from src.ports.repositories.healthity.catalog import ItemsRepository


@dataclass
class CreateItemInput:
    category_id: uuid.UUID
    name: str
    description: str | None = None
    cost: int = 0
    required_level: int = 1
    is_available: bool = True


@dataclass
class UpdateItemInput:
    item_id: uuid.UUID
    name: str | None = None
    description: str | None = None
    cost: int | None = None
    required_level: int | None = None
    is_available: bool | None = None


class CreateItemUseCase:
    def __init__(self, items_repository: ItemsRepository) -> None:
        self._items_repository = items_repository

    async def execute(self, data: CreateItemInput) -> Item:
        item = Item(
            id=uuid.uuid4(),
            category_id=data.category_id,
            name=data.name,
            description=data.description,
            cost=data.cost,
            required_level=data.required_level,
            is_available=data.is_available,
        )
        return await self._items_repository.add(item)


class GetItemUseCase:
    def __init__(self, items_repository: ItemsRepository) -> None:
        self._items_repository = items_repository

    async def execute(self, item_id: uuid.UUID) -> Item:
        item = await self._items_repository.get(item_id)
        if item is None:
            raise EntityNotFoundException(f"Item {item_id} not found")
        return item


class ListItemsUseCase:
    def __init__(self, items_repository: ItemsRepository) -> None:
        self._items_repository = items_repository

    async def execute(self, limit: int = 100, offset: int = 0) -> list[Item]:
        return await self._items_repository.list_all(limit=limit, offset=offset)


class ListAvailableItemsUseCase:
    def __init__(self, items_repository: ItemsRepository) -> None:
        self._items_repository = items_repository

    async def execute(self) -> list[Item]:
        return await self._items_repository.list_available()


class UpdateItemUseCase:
    def __init__(self, items_repository: ItemsRepository) -> None:
        self._items_repository = items_repository

    async def execute(self, data: UpdateItemInput) -> Item:
        item = await self._items_repository.get(data.item_id)
        if item is None:
            raise EntityNotFoundException(f"Item {data.item_id} not found")

        if data.name is not None:
            item.name = data.name
        if data.description is not None:
            item.description = data.description
        if data.cost is not None:
            item.cost = data.cost
        if data.required_level is not None:
            item.required_level = data.required_level
        if data.is_available is not None:
            item.set_availability(data.is_available)

        return await self._items_repository.update(item)


class DeleteItemUseCase:
    def __init__(self, items_repository: ItemsRepository) -> None:
        self._items_repository = items_repository

    async def execute(self, item_id: uuid.UUID) -> None:
        item = await self._items_repository.get(item_id)
        if item is None:
            raise EntityNotFoundException(f"Item {item_id} not found")
        await self._items_repository.delete(item_id)
