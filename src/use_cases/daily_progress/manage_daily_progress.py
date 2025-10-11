import uuid
from dataclasses import dataclass
from datetime import datetime

from src.domain.entities.healthity.activities import DailyProgress
from src.domain.exceptions import EntityNotFoundException
from src.ports.repositories.healthity.activities import DailyProgressRepository


@dataclass
class CreateDailyProgressInput:
    character_id: uuid.UUID
    date: datetime
    experience_gained: int = 0
    level_at_end: int = 1
    mood_average: str | None = None
    behavior_index: int | None = None


@dataclass
class UpdateDailyProgressInput:
    progress_id: uuid.UUID
    experience_gained: int | None = None
    level_at_end: int | None = None
    mood_average: str | None = None
    behavior_index: int | None = None


class CreateDailyProgressUseCase:
    def __init__(self, daily_progress_repository: DailyProgressRepository) -> None:
        self._daily_progress_repository = daily_progress_repository

    async def execute(self, data: CreateDailyProgressInput) -> DailyProgress:
        progress = DailyProgress(
            id=uuid.uuid4(),
            character_id=data.character_id,
            date=data.date,
            experience_gained=data.experience_gained,
            level_at_end=data.level_at_end,
            mood_average=data.mood_average,
            behavior_index=data.behavior_index,
        )
        return await self._daily_progress_repository.upsert(progress)


class ListDailyProgressForCharacterUseCase:
    def __init__(self, daily_progress_repository: DailyProgressRepository) -> None:
        self._daily_progress_repository = daily_progress_repository

    async def execute(self, character_id: uuid.UUID) -> list[DailyProgress]:
        return await self._daily_progress_repository.list_for_character(character_id)


class GetDailyProgressForDayUseCase:
    def __init__(self, daily_progress_repository: DailyProgressRepository) -> None:
        self._daily_progress_repository = daily_progress_repository

    async def execute(self, character_id: uuid.UUID, day: datetime) -> DailyProgress:
        progress = await self._daily_progress_repository.get_for_day(character_id, day)
        if progress is None:
            raise EntityNotFoundException(
                f"Progress for character {character_id} on {day} not found"
            )
        return progress


class GetDailyProgressUseCase:
    def __init__(self, daily_progress_repository: DailyProgressRepository) -> None:
        self._daily_progress_repository = daily_progress_repository

    async def execute(self, progress_id: uuid.UUID) -> DailyProgress:
        progress = await self._daily_progress_repository.get_by_id(progress_id)
        if progress is None:
            raise EntityNotFoundException(f"DailyProgress {progress_id} not found")
        return progress


class UpdateDailyProgressUseCase:
    def __init__(self, daily_progress_repository: DailyProgressRepository) -> None:
        self._daily_progress_repository = daily_progress_repository

    async def execute(self, data: UpdateDailyProgressInput) -> DailyProgress:
        progress = await self._daily_progress_repository.get_by_id(data.progress_id)
        if progress is None:
            raise EntityNotFoundException(f"DailyProgress {data.progress_id} not found")

        if data.experience_gained is not None:
            progress.experience_gained = data.experience_gained
        if data.level_at_end is not None:
            progress.level_at_end = data.level_at_end
        if data.mood_average is not None:
            progress.mood_average = data.mood_average
        if data.behavior_index is not None:
            progress.behavior_index = data.behavior_index

        return await self._daily_progress_repository.update(progress)


class DeleteDailyProgressUseCase:
    def __init__(self, daily_progress_repository: DailyProgressRepository) -> None:
        self._daily_progress_repository = daily_progress_repository

    async def execute(self, progress_id: uuid.UUID) -> None:
        progress = await self._daily_progress_repository.get_by_id(progress_id)
        if progress is None:
            raise EntityNotFoundException(f"DailyProgress {progress_id} not found")
        await self._daily_progress_repository.delete(progress_id)
