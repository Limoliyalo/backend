import uuid
from dataclasses import dataclass

from src.domain.entities.healthity.characters import Character
from src.domain.entities.healthity.activities import MoodHistory
from src.domain.exceptions import EntityNotFoundException
from src.ports.repositories.healthity.characters import CharactersRepository
from src.ports.repositories.healthity.activities import MoodHistoryRepository


@dataclass
class UpdateCharacterInput:
    character_id: uuid.UUID
    name: str | None = None
    sex: str | None = None
    current_mood: str | None = None


class UpdateCharacterUseCase:
    def __init__(
        self,
        characters_repository: CharactersRepository,
        mood_history_repository: MoodHistoryRepository,
    ) -> None:
        self._characters_repository = characters_repository
        self._mood_history_repository = mood_history_repository

    async def execute(self, data: UpdateCharacterInput) -> Character:
        character = await self._characters_repository.get_by_id(data.character_id)
        if character is None:
            raise EntityNotFoundException(f"Character {data.character_id} not found")

        if data.name is not None:
            character.name = data.name
        if data.sex is not None:
            character.sex = data.sex
        if data.current_mood is not None:
            character.set_mood(data.current_mood)

            mood_history = MoodHistory(
                id=uuid.uuid4(),
                character_id=character.id,
                mood=data.current_mood,
                trigger="character_update",
            )
            await self._mood_history_repository.add(mood_history)

        return await self._characters_repository.update(character)
