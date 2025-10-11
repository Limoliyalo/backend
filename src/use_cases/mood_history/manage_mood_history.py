import uuid
from dataclasses import dataclass
from datetime import datetime

from src.domain.entities.healthity.activities import MoodHistory
from src.domain.exceptions import EntityNotFoundException
from src.ports.repositories.healthity.activities import MoodHistoryRepository


@dataclass
class CreateMoodHistoryInput:
    character_id: uuid.UUID
    mood: str
    trigger: str | None = None


class CreateMoodHistoryUseCase:
    def __init__(self, mood_history_repository: MoodHistoryRepository) -> None:
        self._mood_history_repository = mood_history_repository

    async def execute(self, data: CreateMoodHistoryInput) -> MoodHistory:
        mood_history = MoodHistory(
            id=uuid.uuid4(),
            character_id=data.character_id,
            mood=data.mood,
            trigger=data.trigger,
            timestamp=datetime.utcnow(),
        )
        return await self._mood_history_repository.add(mood_history)


class ListMoodHistoryForCharacterUseCase:
    def __init__(self, mood_history_repository: MoodHistoryRepository) -> None:
        self._mood_history_repository = mood_history_repository

    async def execute(
        self, character_id: uuid.UUID, limit: int = 100
    ) -> list[MoodHistory]:
        return await self._mood_history_repository.list_for_character(
            character_id, limit=limit
        )


class GetMoodHistoryUseCase:
    def __init__(self, mood_history_repository: MoodHistoryRepository) -> None:
        self._mood_history_repository = mood_history_repository

    async def execute(self, mood_history_id: uuid.UUID) -> MoodHistory:
        mood_history = await self._mood_history_repository.get_by_id(mood_history_id)
        if mood_history is None:
            raise EntityNotFoundException(f"MoodHistory {mood_history_id} not found")
        return mood_history


@dataclass
class UpdateMoodHistoryInput:
    mood_history_id: uuid.UUID
    mood: str | None = None
    trigger: str | None = None


class UpdateMoodHistoryUseCase:
    def __init__(self, mood_history_repository: MoodHistoryRepository) -> None:
        self._mood_history_repository = mood_history_repository

    async def execute(self, data: UpdateMoodHistoryInput) -> MoodHistory:
        mood_history = await self._mood_history_repository.get_by_id(
            data.mood_history_id
        )
        if mood_history is None:
            raise EntityNotFoundException(
                f"MoodHistory {data.mood_history_id} not found"
            )

        if data.mood is not None:
            mood_history.mood = data.mood
        if data.trigger is not None:
            mood_history.trigger = data.trigger

        return await self._mood_history_repository.update(mood_history)


class DeleteMoodHistoryUseCase:
    def __init__(self, mood_history_repository: MoodHistoryRepository) -> None:
        self._mood_history_repository = mood_history_repository

    async def execute(self, mood_history_id: uuid.UUID) -> None:
        mood_history = await self._mood_history_repository.get_by_id(mood_history_id)
        if mood_history is None:
            raise EntityNotFoundException(f"MoodHistory {mood_history_id} not found")
        await self._mood_history_repository.delete(mood_history_id)
