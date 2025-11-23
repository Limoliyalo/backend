import uuid
from dataclasses import dataclass

from src.domain.entities.healthity.activities import BaseCharacterActivity
from src.domain.exceptions import EntityNotFoundException
from src.ports.repositories.healthity.activities import (
    BaseCharacterActivitiesRepository,
    ActivityTypesRepository,
)


@dataclass
class CreateBaseCharacterActivityInput:
    character_id: uuid.UUID
    activity_type_id: uuid.UUID
    goal: int | None = None


@dataclass
class UpdateBaseCharacterActivityInput:
    activity_id: uuid.UUID
    goal: int | None = None


class ListBaseCharacterActivitiesUseCase:
    def __init__(
        self, base_activities_repository: BaseCharacterActivitiesRepository
    ) -> None:
        self._base_activities_repository = base_activities_repository

    async def execute(self, character_id: uuid.UUID) -> list[BaseCharacterActivity]:
        return await self._base_activities_repository.list_for_character(character_id)


class GetBaseCharacterActivityUseCase:
    def __init__(
        self, base_activities_repository: BaseCharacterActivitiesRepository
    ) -> None:
        self._base_activities_repository = base_activities_repository

    async def execute(self, activity_id: uuid.UUID) -> BaseCharacterActivity:
        activity = await self._base_activities_repository.get_by_id(activity_id)
        if activity is None:
            raise EntityNotFoundException(
                f"BaseCharacterActivity {activity_id} not found"
            )
        return activity


class CreateBaseCharacterActivityUseCase:
    def __init__(
        self,
        base_activities_repository: BaseCharacterActivitiesRepository,
        activity_types_repository: ActivityTypesRepository,
    ) -> None:
        self._base_activities_repository = base_activities_repository
        self._activity_types_repository = activity_types_repository

    async def execute(
        self, data: CreateBaseCharacterActivityInput
    ) -> BaseCharacterActivity:
        # Проверяем, что активность уже не добавлена
        existing = await self._base_activities_repository.get_by_character_and_type(
            data.character_id, data.activity_type_id
        )
        if existing:
            raise ValueError(
                "Activity type already exists in character's base activities"
            )

        # Получаем тип активности для получения дефолтной цели
        activity_type = await self._activity_types_repository.get_by_id(
            data.activity_type_id
        )
        if activity_type is None:
            raise EntityNotFoundException(
                f"ActivityType {data.activity_type_id} not found"
            )

        goal = data.goal if data.goal is not None else activity_type.daily_goal_default

        activity = BaseCharacterActivity(
            id=uuid.uuid4(),
            character_id=data.character_id,
            activity_type_id=data.activity_type_id,
            goal=goal,
        )
        return await self._base_activities_repository.add(activity)


class UpdateBaseCharacterActivityUseCase:
    def __init__(
        self, base_activities_repository: BaseCharacterActivitiesRepository
    ) -> None:
        self._base_activities_repository = base_activities_repository

    async def execute(
        self, data: UpdateBaseCharacterActivityInput
    ) -> BaseCharacterActivity:
        activity = await self._base_activities_repository.get_by_id(data.activity_id)
        if activity is None:
            raise EntityNotFoundException(
                f"BaseCharacterActivity {data.activity_id} not found"
            )

        if data.goal is not None:
            activity.goal = data.goal
            activity.touch()

        return await self._base_activities_repository.update(activity)


class DeleteBaseCharacterActivityUseCase:
    def __init__(
        self, base_activities_repository: BaseCharacterActivitiesRepository
    ) -> None:
        self._base_activities_repository = base_activities_repository

    async def execute(self, activity_id: uuid.UUID) -> None:
        activity = await self._base_activities_repository.get_by_id(activity_id)
        if activity is None:
            raise EntityNotFoundException(
                f"BaseCharacterActivity {activity_id} not found"
            )
        await self._base_activities_repository.delete(activity_id)
