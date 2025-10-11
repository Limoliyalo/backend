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


class UpdateDailyProgressUseCase:
    def __init__(self, daily_progress_repository: DailyProgressRepository) -> None:
        self._daily_progress_repository = daily_progress_repository

    async def execute(self, data: UpdateDailyProgressInput) -> DailyProgress:
        # Нужно добавить get_by_id в репозиторий
        raise NotImplementedError("get_by_id not implemented for DailyProgress")
