import logging
import uuid
from dataclasses import dataclass

from src.domain.entities.healthity.characters import Character
from src.domain.value_objects.telegram_id import TelegramId
from src.ports.repositories.healthity.characters import CharactersRepository

logger = logging.getLogger(__name__)


@dataclass
class CreateCharacterInput:
    user_tg_id: int
    name: str | None = None
    sex: str | None = None
    current_mood: str = "neutral"
    level: int = 1
    total_experience: int = 0


class CreateCharacterUseCase:
    def __init__(self, characters_repository: CharactersRepository) -> None:
        self._characters_repository = characters_repository

    async def execute(self, data: CreateCharacterInput) -> Character:
        logger.debug(f"Creating character for user {data.user_tg_id}")
        character = Character(
            id=uuid.uuid4(),
            user_tg_id=TelegramId(data.user_tg_id),
            name=data.name,
            sex=data.sex,
            current_mood=data.current_mood,
            level=data.level,
            total_experience=data.total_experience,
        )
        logger.debug(f"Character created: {character}")
        result = await self._characters_repository.add(character)
        logger.debug(f"Character added to repository: {result}")
        return result
