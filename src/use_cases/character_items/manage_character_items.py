import uuid
from dataclasses import dataclass

from src.domain.entities.healthity.characters import CharacterItem
from src.domain.exceptions import EntityNotFoundException
from src.ports.repositories.healthity.characters import CharacterItemsRepository


@dataclass
class PurchaseItemInput:
    character_id: uuid.UUID
    item_id: uuid.UUID
    is_equipped: bool = False


class ListCharacterItemsUseCase:
    def __init__(self, character_items_repository: CharacterItemsRepository) -> None:
        self._character_items_repository = character_items_repository

    async def execute(self, character_id: uuid.UUID) -> list[CharacterItem]:
        return await self._character_items_repository.list_for_character(character_id)


class PurchaseItemUseCase:
    def __init__(self, character_items_repository: CharacterItemsRepository) -> None:
        self._character_items_repository = character_items_repository

    async def execute(self, data: PurchaseItemInput) -> CharacterItem:
        item = CharacterItem(
            id=uuid.uuid4(),
            character_id=data.character_id,
            item_id=data.item_id,
            is_equipped=data.is_equipped,
        )
        return await self._character_items_repository.add(item)


class EquipItemUseCase:
    def __init__(self, character_items_repository: CharacterItemsRepository) -> None:
        self._character_items_repository = character_items_repository

    async def execute(self, character_item_id: uuid.UUID) -> CharacterItem:
        item = await self._character_items_repository.get_by_id(character_item_id)
        if item is None:
            raise EntityNotFoundException(
                f"CharacterItem {character_item_id} not found"
            )
        item.equip()
        return await self._character_items_repository.update(item)


class UnequipItemUseCase:
    def __init__(self, character_items_repository: CharacterItemsRepository) -> None:
        self._character_items_repository = character_items_repository

    async def execute(self, character_item_id: uuid.UUID) -> CharacterItem:
        item = await self._character_items_repository.get_by_id(character_item_id)
        if item is None:
            raise EntityNotFoundException(
                f"CharacterItem {character_item_id} not found"
            )
        item.unequip()
        return await self._character_items_repository.update(item)


class RemoveCharacterItemUseCase:
    def __init__(self, character_items_repository: CharacterItemsRepository) -> None:
        self._character_items_repository = character_items_repository

    async def execute(self, character_item_id: uuid.UUID) -> None:
        item = await self._character_items_repository.get_by_id(character_item_id)
        if item is None:
            raise EntityNotFoundException(
                f"CharacterItem {character_item_id} not found"
            )
        await self._character_items_repository.remove(character_item_id)
