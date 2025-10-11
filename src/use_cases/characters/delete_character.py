import uuid

from src.domain.exceptions import EntityNotFoundException
from src.ports.repositories.healthity.characters import CharactersRepository


class DeleteCharacterUseCase:
    def __init__(self, characters_repository: CharactersRepository) -> None:
        self._characters_repository = characters_repository

    async def execute(self, character_id: uuid.UUID) -> None:
        # Проверяем существование перед удалением
        character = await self._characters_repository.get_by_id(character_id)
        if character is None:
            raise EntityNotFoundException(f"Character {character_id} not found")

        await self._characters_repository.delete(character_id)
