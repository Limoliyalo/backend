import uuid
from dataclasses import dataclass
from datetime import datetime

from src.domain.entities.healthity.activities import (
    CharacterActivityHistory,
    DailyProgress,
)
from src.domain.exceptions import EntityNotFoundException
from src.ports.repositories.healthity.activities import (
    DailyActivitiesRepository,
    DailyProgressRepository,
)
from src.ports.repositories.healthity.characters import CharactersRepository

XP_PER_ACTIVITY = 10


def _compute_daily_xp(activities: list[CharacterActivityHistory]) -> int:
    total = 0
    for a in activities:
        if a.goal > 0:
            total += round(min(a.value / a.goal, 1.0) * XP_PER_ACTIVITY)
    return total


@dataclass
class RecalculateDailyXpInput:
    character_id: uuid.UUID
    date: datetime


class RecalculateDailyXpUseCase:
    def __init__(
        self,
        daily_activities_repository: DailyActivitiesRepository,
        daily_progress_repository: DailyProgressRepository,
        characters_repository: CharactersRepository,
    ) -> None:
        self._daily_activities_repository = daily_activities_repository
        self._daily_progress_repository = daily_progress_repository
        self._characters_repository = characters_repository

    async def execute(self, data: RecalculateDailyXpInput) -> DailyProgress:
        date = data.date
        if date.tzinfo is not None:
            date = date.replace(tzinfo=None)
        date_only = date.replace(hour=0, minute=0, second=0, microsecond=0)

        activities = await self._daily_activities_repository.list_for_day(
            data.character_id, date_only
        )
        new_xp = _compute_daily_xp(activities)

        character = await self._characters_repository.get_by_id(data.character_id)
        if character is None:
            raise EntityNotFoundException(
                f"Character {data.character_id} not found"
            )

        existing_progress = await self._daily_progress_repository.get_by_character_date(
            data.character_id, date_only
        )
        old_xp = existing_progress.experience_gained if existing_progress else 0

        character.set_experience(character.total_experience - old_xp + new_xp)
        await self._characters_repository.update(character)

        if existing_progress:
            existing_progress.experience_gained = new_xp
            existing_progress.level_at_end = character.level
            existing_progress.touch()
            return await self._daily_progress_repository.update(existing_progress)

        progress = DailyProgress(
            id=uuid.uuid4(),
            character_id=data.character_id,
            date=date_only,
            experience_gained=new_xp,
            level_at_end=character.level,
        )
        return await self._daily_progress_repository.upsert(progress)
