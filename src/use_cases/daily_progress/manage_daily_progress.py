import uuid
from dataclasses import dataclass
from datetime import datetime

from src.domain.entities.healthity.activities import DailyProgress, MoodHistory
from src.domain.exceptions import EntityNotFoundException
from src.ports.repositories.healthity.activities import (
    DailyProgressRepository,
    MoodHistoryRepository,
)
from src.ports.repositories.healthity.characters import CharactersRepository


@dataclass
class CreateDailyProgressInput:
    character_id: uuid.UUID
    date: datetime
    experience_gained: int = 0
    mood_average: str | None = None
    behavior_index: int | None = None


@dataclass
class UpdateDailyProgressInput:
    progress_id: uuid.UUID
    experience_gained: int | None = None
    mood_average: str | None = None
    behavior_index: int | None = None


class CreateDailyProgressUseCase:
    def __init__(
        self,
        daily_progress_repository: DailyProgressRepository,
        characters_repository: CharactersRepository,
        mood_history_repository: MoodHistoryRepository,
    ) -> None:
        self._daily_progress_repository = daily_progress_repository
        self._characters_repository = characters_repository
        self._mood_history_repository = mood_history_repository

    async def execute(self, data: CreateDailyProgressInput) -> DailyProgress:

        date = data.date
        if date.tzinfo is not None:
            date = date.replace(tzinfo=None)

        date_only = date.replace(hour=0, minute=0, second=0, microsecond=0)

        character = await self._characters_repository.get_by_id(data.character_id)
        if character is None:
            raise EntityNotFoundException(f"Character {data.character_id} not found")

        character.add_experience(data.experience_gained)

        if data.mood_average is not None:
            character.set_mood(data.mood_average)

            mood_history = MoodHistory(
                id=uuid.uuid4(),
                character_id=character.id,
                mood=data.mood_average,
                trigger="daily_progress_update",
            )
            await self._mood_history_repository.add(mood_history)

        await self._characters_repository.update(character)

        existing_progress = await self._daily_progress_repository.get_by_character_date(
            data.character_id, date_only
        )

        if existing_progress:

            existing_progress.experience_gained += data.experience_gained
            existing_progress.level_at_end = character.level
            existing_progress.mood_average = data.mood_average
            existing_progress.behavior_index = data.behavior_index
            existing_progress.touch()

            if (
                data.mood_average is not None
                and data.mood_average != existing_progress.mood_average
            ):
                character.set_mood(data.mood_average)

                mood_history = MoodHistory(
                    id=uuid.uuid4(),
                    character_id=character.id,
                    mood=data.mood_average,
                    trigger="daily_progress_update",
                )
                await self._mood_history_repository.add(mood_history)
                await self._characters_repository.update(character)

            return await self._daily_progress_repository.update(existing_progress)
        else:

            progress = DailyProgress(
                id=uuid.uuid4(),
                character_id=data.character_id,
                date=date_only,
                experience_gained=data.experience_gained,
                level_at_end=character.level,
                mood_average=data.mood_average,
                behavior_index=data.behavior_index,
            )
            return await self._daily_progress_repository.upsert(progress)


class ListDailyProgressForCharacterUseCase:
    def __init__(self, daily_progress_repository: DailyProgressRepository) -> None:
        self._daily_progress_repository = daily_progress_repository

    async def execute(self, character_id: uuid.UUID) -> list[DailyProgress]:
        return await self._daily_progress_repository.list_for_character(character_id)


class ListDailyProgressForDateRangeUseCase:
    def __init__(self, daily_progress_repository: DailyProgressRepository) -> None:
        self._daily_progress_repository = daily_progress_repository

    async def execute(
        self, character_id: uuid.UUID, start_date: datetime, end_date: datetime
    ) -> list[DailyProgress]:

        normalized_start = start_date
        if normalized_start.tzinfo is not None:
            normalized_start = normalized_start.replace(tzinfo=None)

        normalized_end = end_date
        if normalized_end.tzinfo is not None:
            normalized_end = normalized_end.replace(tzinfo=None)

        start_date_only = normalized_start.replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        end_date_only = normalized_end.replace(
            hour=0, minute=0, second=0, microsecond=0
        )

        return await self._daily_progress_repository.list_for_date_range(
            character_id, start_date_only, end_date_only
        )


class GetDailyProgressForDayUseCase:
    def __init__(self, daily_progress_repository: DailyProgressRepository) -> None:
        self._daily_progress_repository = daily_progress_repository

    async def execute(self, character_id: uuid.UUID, day: datetime) -> DailyProgress:

        normalized_day = day
        if normalized_day.tzinfo is not None:
            normalized_day = normalized_day.replace(tzinfo=None)

        date_only = normalized_day.replace(hour=0, minute=0, second=0, microsecond=0)

        progress = await self._daily_progress_repository.get_for_day(
            character_id, date_only
        )
        if progress is None:
            raise EntityNotFoundException(
                f"Progress for character {character_id} on {date_only} not found"
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
