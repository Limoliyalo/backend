import uuid
from dataclasses import dataclass

from src.domain.entities.healthity.characters import CharacterBackground
from src.domain.entities.healthity.transactions import Transaction
from src.domain.exceptions import EntityNotFoundException
from src.domain.value_objects.telegram_id import TelegramId
from src.ports.repositories.healthity.catalog import BackgroundsRepository
from src.ports.repositories.healthity.characters import CharacterBackgroundsRepository
from src.ports.repositories.healthity.transactions import TransactionsRepository
from src.ports.repositories.healthity.users import UsersRepository


@dataclass
class PurchaseBackgroundInput:
    character_id: uuid.UUID
    background_id: uuid.UUID
    is_active: bool = False
    is_favorite: bool = False


class ListCharacterBackgroundsUseCase:
    def __init__(
        self, character_backgrounds_repository: CharacterBackgroundsRepository
    ) -> None:
        self._character_backgrounds_repository = character_backgrounds_repository

    async def execute(self, character_id: uuid.UUID) -> list[CharacterBackground]:
        return await self._character_backgrounds_repository.list_for_character(
            character_id
        )


class GetCharacterBackgroundUseCase:
    def __init__(
        self, character_backgrounds_repository: CharacterBackgroundsRepository
    ) -> None:
        self._character_backgrounds_repository = character_backgrounds_repository

    async def execute(self, character_background_id: uuid.UUID) -> CharacterBackground:
        background = await self._character_backgrounds_repository.get_by_id(
            character_background_id
        )
        if background is None:
            raise EntityNotFoundException(
                f"CharacterBackground {character_background_id} not found"
            )
        return background


class PurchaseBackgroundUseCase:
    def __init__(
        self, character_backgrounds_repository: CharacterBackgroundsRepository
    ) -> None:
        self._character_backgrounds_repository = character_backgrounds_repository

    async def execute(self, data: PurchaseBackgroundInput) -> CharacterBackground:
        background = CharacterBackground(
            id=uuid.uuid4(),
            character_id=data.character_id,
            background_id=data.background_id,
            is_active=data.is_active,
            is_favorite=data.is_favorite,
        )
        return await self._character_backgrounds_repository.add(background)


class EquipBackgroundUseCase:
    def __init__(
        self, character_backgrounds_repository: CharacterBackgroundsRepository
    ) -> None:
        self._character_backgrounds_repository = character_backgrounds_repository

    async def execute(self, character_background_id: uuid.UUID) -> CharacterBackground:
        background = await self._character_backgrounds_repository.get_by_id(
            character_background_id
        )
        if background is None:
            raise EntityNotFoundException(
                f"CharacterBackground {character_background_id} not found"
            )

        existing_backgrounds = (
            await self._character_backgrounds_repository.list_for_character(
                background.character_id
            )
        )
        for existing_background in existing_backgrounds:
            if (
                existing_background.id != background.id
                and existing_background.is_active
            ):
                existing_background.deactivate()
                await self._character_backgrounds_repository.update(existing_background)

        background.activate()
        return await self._character_backgrounds_repository.update(background)


class UnequipBackgroundUseCase:
    def __init__(
        self, character_backgrounds_repository: CharacterBackgroundsRepository
    ) -> None:
        self._character_backgrounds_repository = character_backgrounds_repository

    async def execute(self, character_background_id: uuid.UUID) -> CharacterBackground:
        background = await self._character_backgrounds_repository.get_by_id(
            character_background_id
        )
        if background is None:
            raise EntityNotFoundException(
                f"CharacterBackground {character_background_id} not found"
            )
        background.deactivate()
        return await self._character_backgrounds_repository.update(background)


@dataclass
class UpdateCharacterBackgroundInput:
    character_background_id: uuid.UUID
    is_active: bool | None = None
    is_favorite: bool | None = None


class UpdateCharacterBackgroundUseCase:
    def __init__(
        self, character_backgrounds_repository: CharacterBackgroundsRepository
    ) -> None:
        self._character_backgrounds_repository = character_backgrounds_repository

    async def execute(
        self, data: UpdateCharacterBackgroundInput
    ) -> CharacterBackground:
        background = await self._character_backgrounds_repository.get_by_id(
            data.character_background_id
        )
        if background is None:
            raise EntityNotFoundException(
                f"CharacterBackground {data.character_background_id} not found"
            )

        if data.is_active is not None:
            if data.is_active:

                existing_backgrounds = (
                    await self._character_backgrounds_repository.list_for_character(
                        background.character_id
                    )
                )
                for existing_background in existing_backgrounds:
                    if (
                        existing_background.id != background.id
                        and existing_background.is_active
                    ):
                        existing_background.deactivate()
                        await self._character_backgrounds_repository.update(
                            existing_background
                        )

                background.activate()
            else:
                background.deactivate()

        if data.is_favorite is not None:
            background.is_favorite = data.is_favorite

        return await self._character_backgrounds_repository.update(background)


class RemoveCharacterBackgroundUseCase:
    def __init__(
        self, character_backgrounds_repository: CharacterBackgroundsRepository
    ) -> None:
        self._character_backgrounds_repository = character_backgrounds_repository

    async def execute(self, character_background_id: uuid.UUID) -> None:
        background = await self._character_backgrounds_repository.get_by_id(
            character_background_id
        )
        if background is None:
            raise EntityNotFoundException(
                f"CharacterBackground {character_background_id} not found"
            )
        await self._character_backgrounds_repository.remove(character_background_id)


class ToggleFavouriteBackgroundUseCase:
    def __init__(
        self, character_backgrounds_repository: CharacterBackgroundsRepository
    ) -> None:
        self._character_backgrounds_repository = character_backgrounds_repository

    async def execute(self, character_background_id: uuid.UUID) -> CharacterBackground:
        background = await self._character_backgrounds_repository.get_by_id(
            character_background_id
        )
        if background is None:
            raise EntityNotFoundException(
                f"CharacterBackground {character_background_id} not found"
            )
        background.toggle_favourite()
        return await self._character_backgrounds_repository.update(background)


@dataclass
class PurchaseBackgroundWithBalanceInput:
    user_tg_id: int
    character_id: uuid.UUID
    background_id: uuid.UUID


class PurchaseBackgroundWithBalanceUseCase:
    """Покупка фона с проверкой баланса и списанием средств."""

    def __init__(
        self,
        character_backgrounds_repository: CharacterBackgroundsRepository,
        backgrounds_repository: BackgroundsRepository,
        users_repository: UsersRepository,
        transactions_repository: TransactionsRepository,
    ) -> None:
        self._character_backgrounds_repository = character_backgrounds_repository
        self._backgrounds_repository = backgrounds_repository
        self._users_repository = users_repository
        self._transactions_repository = transactions_repository

    async def execute(
        self, data: PurchaseBackgroundWithBalanceInput
    ) -> CharacterBackground:

        background = await self._backgrounds_repository.get_by_id(data.background_id)
        if background is None:
            raise EntityNotFoundException(f"Background {data.background_id} not found")

        if not background.is_available:
            raise ValueError("Background is not available for purchase")

        existing_backgrounds = (
            await self._character_backgrounds_repository.list_for_character(
                data.character_id
            )
        )
        if any(cb.background_id == data.background_id for cb in existing_backgrounds):
            raise ValueError("Background already purchased")

        telegram_id = TelegramId(data.user_tg_id)
        user = await self._users_repository.get_by_telegram_id(telegram_id)
        if user is None:
            raise EntityNotFoundException(f"User {data.user_tg_id} not found")

        user.withdraw(background.cost)
        updated_user = await self._users_repository.update(user)

        character_background = CharacterBackground(
            id=uuid.uuid4(),
            character_id=data.character_id,
            background_id=data.background_id,
            is_active=False,
            is_favorite=False,
        )
        created_background = await self._character_backgrounds_repository.add(
            character_background
        )

        transaction = Transaction(
            id=uuid.uuid4(),
            user_tg_id=telegram_id,
            amount=-background.cost,
            balance_after=updated_user.balance,
            type="purchase_background",
            related_item_id=data.background_id,
            description=f"Покупка фона: {background.name}",
        )
        await self._transactions_repository.add(transaction)

        return created_background
