import uuid
from dataclasses import dataclass

from src.domain.entities.healthity.characters import CharacterItem
from src.domain.entities.healthity.transactions import Transaction
from src.domain.exceptions import EntityNotFoundException
from src.ports.repositories.healthity.catalog import ItemsRepository
from src.ports.repositories.healthity.characters import CharacterItemsRepository
from src.ports.repositories.healthity.transactions import TransactionsRepository
from src.ports.repositories.healthity.users import UsersRepository


@dataclass
class PurchaseItemInput:
    character_id: uuid.UUID
    item_id: uuid.UUID
    is_active: bool = False
    is_favorite: bool = False


class ListCharacterItemsUseCase:
    def __init__(self, character_items_repository: CharacterItemsRepository) -> None:
        self._character_items_repository = character_items_repository

    async def execute(self, character_id: uuid.UUID) -> list[CharacterItem]:
        return await self._character_items_repository.list_for_character(character_id)


class GetCharacterItemUseCase:
    def __init__(self, character_items_repository: CharacterItemsRepository) -> None:
        self._character_items_repository = character_items_repository

    async def execute(self, character_item_id: uuid.UUID) -> CharacterItem:
        item = await self._character_items_repository.get_by_id(character_item_id)
        if item is None:
            raise EntityNotFoundException(
                f"CharacterItem {character_item_id} not found"
            )
        return item


class PurchaseItemUseCase:
    def __init__(self, character_items_repository: CharacterItemsRepository) -> None:
        self._character_items_repository = character_items_repository

    async def execute(self, data: PurchaseItemInput) -> CharacterItem:
        item = CharacterItem(
            id=uuid.uuid4(),
            character_id=data.character_id,
            item_id=data.item_id,
            is_active=data.is_active,
            is_favorite=data.is_favorite,
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


@dataclass
class UpdateCharacterItemInput:
    character_item_id: uuid.UUID
    is_active: bool | None = None
    is_favorite: bool | None = None


class UpdateCharacterItemUseCase:
    def __init__(self, character_items_repository: CharacterItemsRepository) -> None:
        self._character_items_repository = character_items_repository

    async def execute(self, data: UpdateCharacterItemInput) -> CharacterItem:
        item = await self._character_items_repository.get_by_id(data.character_item_id)
        if item is None:
            raise EntityNotFoundException(
                f"CharacterItem {data.character_item_id} not found"
            )

        if data.is_active is not None:
            if data.is_active:
                item.equip()
            else:
                item.unequip()

        if data.is_favorite is not None:
            item.is_favorite = data.is_favorite

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


@dataclass
class ToggleFavoriteItemInput:
    character_id: uuid.UUID
    item_id: uuid.UUID


class ToggleFavoriteItemUseCase:
    """Переключить избранное для предмета (создает запись если её нет)"""

    def __init__(
        self,
        character_items_repository: CharacterItemsRepository,
        items_repository: ItemsRepository,
    ) -> None:
        self._character_items_repository = character_items_repository
        self._items_repository = items_repository

    async def execute(self, data: ToggleFavoriteItemInput) -> CharacterItem:
        # Проверяем, что итем существует
        item = await self._items_repository.get(data.item_id)
        if item is None:
            raise EntityNotFoundException(f"Item {data.item_id} not found")

        # Проверяем, есть ли уже запись об этом предмете
        existing_items = await self._character_items_repository.list_for_character(
            data.character_id
        )
        existing_item = next(
            (ci for ci in existing_items if ci.item_id == data.item_id), None
        )

        if existing_item:
            # Если запись уже существует, переключаем is_favorite
            existing_item.toggle_favorite()
            return await self._character_items_repository.update(existing_item)
        else:
            # Создаем новую запись с is_favorite=True, is_purchased=False, is_active=False
            character_item = CharacterItem(
                id=uuid.uuid4(),
                character_id=data.character_id,
                item_id=data.item_id,
                is_active=False,
                is_favorite=True,
                is_purchased=False,
            )
            return await self._character_items_repository.add(character_item)


@dataclass
class PurchaseItemWithBalanceInput:
    user_tg_id: int
    character_id: uuid.UUID
    item_id: uuid.UUID


class PurchaseItemWithBalanceUseCase:
    """Покупка предмета с проверкой баланса и списанием средств."""

    def __init__(
        self,
        character_items_repository: CharacterItemsRepository,
        items_repository: ItemsRepository,
        users_repository: UsersRepository,
        transactions_repository: TransactionsRepository,
    ) -> None:
        self._character_items_repository = character_items_repository
        self._items_repository = items_repository
        self._users_repository = users_repository
        self._transactions_repository = transactions_repository

    async def execute(self, data: PurchaseItemWithBalanceInput) -> CharacterItem:

        # Получаем предмет
        item = await self._items_repository.get(data.item_id)
        if item is None:
            raise EntityNotFoundException(f"Item {data.item_id} not found")

        if not item.is_available:
            raise ValueError("Item is not available for purchase")

        # Проверяем, есть ли уже запись об этом предмете
        existing_items = await self._character_items_repository.list_for_character(
            data.character_id
        )
        existing_item = next(
            (ci for ci in existing_items if ci.item_id == data.item_id), None
        )

        # Получаем пользователя и проверяем баланс
        user = await self._users_repository.get_by_telegram_id(data.user_tg_id)
        if user is None:
            raise EntityNotFoundException(f"User {data.user_tg_id} not found")

        # Проверяем достаточность средств
        if user.balance < item.cost:
            raise ValueError(
                f"Insufficient funds. Required: {item.cost}, Available: {user.balance}"
            )

        # Если предмет уже есть в избранном, просто помечаем как купленный
        if existing_item:
            if existing_item.is_purchased:
                raise ValueError("Item already purchased")
            existing_item.is_purchased = True
            updated_item = await self._character_items_repository.update(existing_item)
            # Списываем деньги с баланса пользователя
            user.withdraw(item.cost)
            updated_user = await self._users_repository.update(user)
            created_item = updated_item
        else:
            # Списываем деньги с баланса пользователя
            user.withdraw(item.cost)
            updated_user = await self._users_repository.update(user)

            character_item = CharacterItem(
                id=uuid.uuid4(),
                character_id=data.character_id,
                item_id=data.item_id,
                is_active=False,
                is_favorite=False,
                is_purchased=True,
            )
            created_item = await self._character_items_repository.add(character_item)

        transaction = Transaction(
            id=uuid.uuid4(),
            user_tg_id=data.user_tg_id,
            amount=-item.cost,
            balance_after=updated_user.balance,
            type="purchase_item",
            related_item_id=data.item_id,
            description=f"Покупка предмета: {item.name}",
        )
        await self._transactions_repository.add(transaction)

        return created_item
