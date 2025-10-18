import uuid
from dataclasses import dataclass
from datetime import datetime

from src.domain.entities.healthity.activities import DailyActivity
from src.domain.exceptions import EntityNotFoundException
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

        date = data.date
        if date.tzinfo is not None:
            date = date.replace(tzinfo=None)

        date_only = date.replace(hour=0, minute=0, second=0, microsecond=0)

        existing_activity = (
            await self._daily_activities_repository.get_by_character_activity_date(
                data.character_id, data.activity_type_id, date_only
            )
        )

        if existing_activity:

            existing_activity.value += data.value
            existing_activity.goal = data.goal
            existing_activity.notes = data.notes
            existing_activity.touch()
            return await self._daily_activities_repository.update(existing_activity)
        else:

            activity = DailyActivity(
                id=uuid.uuid4(),
                character_id=data.character_id,
                activity_type_id=data.activity_type_id,
                date=date_only,
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

        normalized_day = day
        if normalized_day.tzinfo is not None:
            normalized_day = normalized_day.replace(tzinfo=None)

        date_only = normalized_day.replace(hour=0, minute=0, second=0, microsecond=0)

        return await self._daily_activities_repository.list_for_day(
            character_id, date_only
        )


class GetDailyActivityUseCase:
    def __init__(self, daily_activities_repository: DailyActivitiesRepository) -> None:
        self._daily_activities_repository = daily_activities_repository

    async def execute(self, activity_id: uuid.UUID) -> DailyActivity:
        activity = await self._daily_activities_repository.get_by_id(activity_id)
        if activity is None:
            raise EntityNotFoundException(f"DailyActivity {activity_id} not found")
        return activity


class UpdateDailyActivityUseCase:
    def __init__(self, daily_activities_repository: DailyActivitiesRepository) -> None:
        self._daily_activities_repository = daily_activities_repository

    async def execute(self, data: UpdateDailyActivityInput) -> DailyActivity:
        activity = await self._daily_activities_repository.get_by_id(data.activity_id)
        if activity is None:
            raise EntityNotFoundException(f"DailyActivity {data.activity_id} not found")

        if data.value is not None:
            activity.value = data.value
        if data.goal is not None:
            activity.goal = data.goal
        if data.notes is not None:
            activity.notes = data.notes

        return await self._daily_activities_repository.update(activity)


class DeleteDailyActivityUseCase:
    def __init__(self, daily_activities_repository: DailyActivitiesRepository) -> None:
        self._daily_activities_repository = daily_activities_repository

    async def execute(self, activity_id: uuid.UUID) -> None:
        activity = await self._daily_activities_repository.get_by_id(activity_id)
        if activity is None:
            raise EntityNotFoundException(f"DailyActivity {activity_id} not found")
        await self._daily_activities_repository.delete(activity_id)
