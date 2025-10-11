import uuid

from src.domain.entities.healthity.characters import Character
from src.domain.exceptions import EntityNotFoundException
from src.domain.value_objects.telegram_id import TelegramId
from src.ports.repositories.healthity.characters import CharactersRepository


class GetCharacterByIdUseCase:
    def __init__(self, characters_repository: CharactersRepository) -> None:
        self._characters_repository = characters_repository

    async def execute(self, character_id: uuid.UUID) -> Character:
        character = await self._characters_repository.get_by_id(character_id)
        if character is None:
            raise EntityNotFoundException(f"Character {character_id} not found")
        return character


class GetCharacterByUserUseCase:
    def __init__(self, characters_repository: CharactersRepository) -> None:
        self._characters_repository = characters_repository

    async def execute(self, user_tg_id: int) -> Character:
        character = await self._characters_repository.get_by_user(
            TelegramId(user_tg_id)
        )
        if character is None:
            raise EntityNotFoundException(f"Character for user {user_tg_id} not found")
        return character


class ListCharactersUseCase:
    def __init__(self, characters_repository: CharactersRepository) -> None:
        self._characters_repository = characters_repository

    async def execute(self, limit: int = 100, offset: int = 0) -> list[Character]:
        return await self._characters_repository.list_all(limit=limit, offset=offset)
