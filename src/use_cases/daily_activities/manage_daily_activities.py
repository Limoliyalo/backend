import uuid
from dataclasses import dataclass
from datetime import datetime

from src.domain.entities.healthity.activities import DailyActivity
from src.ports.repositories.healthity.activities import DailyActivitiesRepository


@dataclass
class CreateDailyActivityInput:
    character_id: uuid.UUID
    activity_type_id: uuid.UUID
    date: datetime
    value: int = 0
    goal: int = 1
    notes: str | None = None


@dataclass
class UpdateDailyActivityInput:
    activity_id: uuid.UUID
    value: int | None = None
    goal: int | None = None
    notes: str | None = None


class CreateDailyActivityUseCase:
    def __init__(self, daily_activities_repository: DailyActivitiesRepository) -> None:
        self._daily_activities_repository = daily_activities_repository

    async def execute(self, data: CreateDailyActivityInput) -> DailyActivity:
        activity = DailyActivity(
            id=uuid.uuid4(),
            character_id=data.character_id,
            activity_type_id=data.activity_type_id,
            date=data.date,
            value=data.value,
            goal=data.goal,
            notes=data.notes,
        )
        return await self._daily_activities_repository.upsert(activity)


class ListDailyActivitiesForDayUseCase:
    def __init__(self, daily_activities_repository: DailyActivitiesRepository) -> None:
        self._daily_activities_repository = daily_activities_repository

    async def execute(
        self, character_id: uuid.UUID, day: datetime
    ) -> list[DailyActivity]:
        return await self._daily_activities_repository.list_for_day(character_id, day)


class UpdateDailyActivityUseCase:
    def __init__(self, daily_activities_repository: DailyActivitiesRepository) -> None:
        self._daily_activities_repository = daily_activities_repository

    async def execute(self, data: UpdateDailyActivityInput) -> DailyActivity:
        # Нужно получить существующую активность (добавить get_by_id)
        raise NotImplementedError("get_by_id not implemented for DailyActivity")
