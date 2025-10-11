import uuid
from dataclasses import dataclass

from src.domain.entities.healthity.activities import ActivityType
from src.domain.exceptions import EntityNotFoundException
from src.ports.repositories.healthity.activities import ActivityTypesRepository


@dataclass
class CreateActivityTypeInput:
    name: str
    unit: str
    color: str | None = None
    daily_goal_default: int = 0


class CreateActivityTypeUseCase:
    def __init__(self, activity_types_repository: ActivityTypesRepository) -> None:
        self._activity_types_repository = activity_types_repository

    async def execute(self, data: CreateActivityTypeInput) -> ActivityType:
        activity_type = ActivityType(
            id=uuid.uuid4(),
            name=data.name,
            unit=data.unit,
            color=data.color,
            daily_goal_default=data.daily_goal_default,
        )
        return await self._activity_types_repository.add(activity_type)


class GetActivityTypeUseCase:
    def __init__(self, activity_types_repository: ActivityTypesRepository) -> None:
        self._activity_types_repository = activity_types_repository

    async def execute(self, activity_type_id: uuid.UUID) -> ActivityType:
        activity_type = await self._activity_types_repository.get_by_id(
            activity_type_id
        )
        if activity_type is None:
            raise EntityNotFoundException(f"ActivityType {activity_type_id} not found")
        return activity_type


class GetActivityTypeByNameUseCase:
    def __init__(self, activity_types_repository: ActivityTypesRepository) -> None:
        self._activity_types_repository = activity_types_repository

    async def execute(self, name: str) -> ActivityType:
        activity_type = await self._activity_types_repository.get_by_name(name)
        if activity_type is None:
            raise EntityNotFoundException(f"ActivityType '{name}' not found")
        return activity_type


class ListActivityTypesUseCase:
    def __init__(self, activity_types_repository: ActivityTypesRepository) -> None:
        self._activity_types_repository = activity_types_repository

    async def execute(self) -> list[ActivityType]:
        return await self._activity_types_repository.list_all()


@dataclass
class UpdateActivityTypeInput:
    activity_type_id: uuid.UUID
    name: str | None = None
    unit: str | None = None
    color: str | None = None
    daily_goal_default: int | None = None


class UpdateActivityTypeUseCase:
    def __init__(self, activity_types_repository: ActivityTypesRepository) -> None:
        self._activity_types_repository = activity_types_repository

    async def execute(self, data: UpdateActivityTypeInput) -> ActivityType:
        activity_type = await self._activity_types_repository.get_by_id(
            data.activity_type_id
        )
        if activity_type is None:
            raise EntityNotFoundException(
                f"ActivityType {data.activity_type_id} not found"
            )

        if data.name is not None:
            activity_type.name = data.name
        if data.unit is not None:
            activity_type.unit = data.unit
        if data.color is not None:
            activity_type.color = data.color
        if data.daily_goal_default is not None:
            activity_type.daily_goal_default = data.daily_goal_default

        return await self._activity_types_repository.update(activity_type)


class DeleteActivityTypeUseCase:
    def __init__(self, activity_types_repository: ActivityTypesRepository) -> None:
        self._activity_types_repository = activity_types_repository

    async def execute(self, activity_type_id: uuid.UUID) -> None:
        activity_type = await self._activity_types_repository.get_by_id(
            activity_type_id
        )
        if activity_type is None:
            raise EntityNotFoundException(f"ActivityType {activity_type_id} not found")
        await self._activity_types_repository.delete(activity_type_id)
