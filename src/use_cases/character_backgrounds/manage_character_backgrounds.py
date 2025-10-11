import uuid
from dataclasses import dataclass

from src.domain.entities.healthity.characters import CharacterBackground
from src.domain.exceptions import EntityNotFoundException
from src.ports.repositories.healthity.characters import CharacterBackgroundsRepository


@dataclass
class PurchaseBackgroundInput:
    character_id: uuid.UUID
    background_id: uuid.UUID
    is_active: bool = False


class ListCharacterBackgroundsUseCase:
    def __init__(
        self, character_backgrounds_repository: CharacterBackgroundsRepository
    ) -> None:
        self._character_backgrounds_repository = character_backgrounds_repository

    async def execute(self, character_id: uuid.UUID) -> list[CharacterBackground]:
        return await self._character_backgrounds_repository.list_for_character(
            character_id
        )


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
        )
        return await self._character_backgrounds_repository.add(background)


class ActivateBackgroundUseCase:
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
        background.activate()
        return await self._character_backgrounds_repository.update(background)


class DeactivateBackgroundUseCase:
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
