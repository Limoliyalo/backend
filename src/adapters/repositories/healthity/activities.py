from collections.abc import Callable
import uuid
from datetime import datetime

from sqlalchemy import delete, select

from src.adapters.database.models.activities import (
    ActivityTypeModel,
    DailyActivityModel,
    DailyProgressModel,
    MoodHistoryModel,
)
from src.adapters.database.uow import AbstractUnitOfWork
from src.adapters.repositories.base import SQLAlchemyRepository
from src.domain.entities.healthity.activities import (
    ActivityType,
    DailyActivity,
    DailyProgress,
    MoodHistory,
)
from src.ports.repositories.healthity.activities import (
    ActivityTypesRepository,
    DailyActivitiesRepository,
    DailyProgressRepository,
    MoodHistoryRepository,
)


class SQLAlchemyActivityTypesRepository(
    SQLAlchemyRepository[ActivityTypeModel], ActivityTypesRepository
):
    model = ActivityTypeModel

    def __init__(self, uow_factory: Callable[[], AbstractUnitOfWork]) -> None:
        super().__init__(uow_factory)

    async def list_all(self) -> list[ActivityType]:
        models = await self.list()
        return [self._to_domain(model) for model in models]

    async def get_by_name(self, name: str) -> ActivityType | None:
        model = await self.first(filters={"name": name})
        if model is None:
            return None
        return self._to_domain(model)

    async def add(self, activity_type: ActivityType) -> ActivityType:
        model = ActivityTypeModel(
            id=activity_type.id,
            name=activity_type.name,
            unit=activity_type.unit,
            color=activity_type.color,
            daily_goal_default=activity_type.daily_goal_default,
            created_at=activity_type.created_at,
        )
        saved_model = await super().add(model)
        return self._to_domain(saved_model)

    @staticmethod
    def _to_domain(model: ActivityTypeModel) -> ActivityType:
        return ActivityType(
            id=model.id,
            name=model.name,
            unit=model.unit,
            color=model.color,
            daily_goal_default=model.daily_goal_default,
            created_at=model.created_at,
        )


class SQLAlchemyDailyActivitiesRepository(
    SQLAlchemyRepository[DailyActivityModel], DailyActivitiesRepository
):
    model = DailyActivityModel

    def __init__(self, uow_factory: Callable[[], AbstractUnitOfWork]) -> None:
        super().__init__(uow_factory)

    async def list_for_day(
        self, character_id: uuid.UUID, day: datetime
    ) -> list[DailyActivity]:
        models = await self.list(filters={"character_id": character_id, "date": day})
        return [self._to_domain(model) for model in models]

    async def upsert(self, activity: DailyActivity) -> DailyActivity:
        async with self._uow() as uow:
            model = await uow.session.get(DailyActivityModel, activity.id)
            if model is None:
                model = DailyActivityModel(
                    id=activity.id,
                    character_id=activity.character_id,
                    activity_type_id=activity.activity_type_id,
                    date=activity.date,
                    value=activity.value,
                    goal=activity.goal,
                    notes=activity.notes,
                    created_at=activity.created_at,
                    updated_at=activity.updated_at,
                )
                uow.session.add(model)
            else:
                model.value = activity.value
                model.goal = activity.goal
                model.notes = activity.notes

            await uow.session.flush()
            await uow.session.refresh(model)
            return self._to_domain(model)

    @staticmethod
    def _to_domain(model: DailyActivityModel) -> DailyActivity:
        return DailyActivity(
            id=model.id,
            character_id=model.character_id,
            activity_type_id=model.activity_type_id,
            date=model.date,
            value=model.value,
            goal=model.goal,
            notes=model.notes,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )


class SQLAlchemyDailyProgressRepository(
    SQLAlchemyRepository[DailyProgressModel], DailyProgressRepository
):
    model = DailyProgressModel

    def __init__(self, uow_factory: Callable[[], AbstractUnitOfWork]) -> None:
        super().__init__(uow_factory)

    async def get_for_day(
        self, character_id: uuid.UUID, day: datetime
    ) -> DailyProgress | None:
        model = await self.first(filters={"character_id": character_id, "date": day})
        if model is None:
            return None
        return self._to_domain(model)

    async def upsert(self, progress: DailyProgress) -> DailyProgress:
        async with self._uow() as uow:
            model = await uow.session.get(DailyProgressModel, progress.id)
            if model is None:
                model = DailyProgressModel(
                    id=progress.id,
                    character_id=progress.character_id,
                    date=progress.date,
                    experience_gained=progress.experience_gained,
                    level_at_end=progress.level_at_end,
                    mood_average=progress.mood_average,
                    behavior_index=progress.behavior_index,
                    created_at=progress.created_at,
                    updated_at=progress.updated_at,
                )
                uow.session.add(model)
            else:
                model.experience_gained = progress.experience_gained
                model.level_at_end = progress.level_at_end
                model.mood_average = progress.mood_average
                model.behavior_index = progress.behavior_index

            await uow.session.flush()
            await uow.session.refresh(model)
            return self._to_domain(model)

    @staticmethod
    def _to_domain(model: DailyProgressModel) -> DailyProgress:
        return DailyProgress(
            id=model.id,
            character_id=model.character_id,
            date=model.date,
            experience_gained=model.experience_gained,
            level_at_end=model.level_at_end,
            mood_average=model.mood_average,
            behavior_index=model.behavior_index,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )


class SQLAlchemyMoodHistoryRepository(
    SQLAlchemyRepository[MoodHistoryModel], MoodHistoryRepository
):
    model = MoodHistoryModel

    def __init__(self, uow_factory: Callable[[], AbstractUnitOfWork]) -> None:
        super().__init__(uow_factory)

    async def list_recent(
        self, character_id: uuid.UUID, limit: int = 20
    ) -> list[MoodHistory]:
        async with self._uow() as uow:
            result = await uow.session.execute(
                select(MoodHistoryModel)
                .where(MoodHistoryModel.character_id == character_id)
                .order_by(MoodHistoryModel.timestamp.desc())
                .limit(limit)
            )
            models = result.scalars().all()
        return [self._to_domain(model) for model in models]

    async def list_for_character(
        self, character_id: uuid.UUID, limit: int = 100
    ) -> list[MoodHistory]:
        async with self._uow() as uow:
            result = await uow.session.execute(
                select(MoodHistoryModel)
                .where(MoodHistoryModel.character_id == character_id)
                .order_by(MoodHistoryModel.timestamp.desc())
                .limit(limit)
            )
            models = result.scalars().all()
        return [self._to_domain(model) for model in models]

    async def get_by_id(self, mood_id: uuid.UUID) -> MoodHistory | None:
        model = await self.first(filters={"id": mood_id})
        if model is None:
            return None
        return self._to_domain(model)

    async def add(self, mood: MoodHistory) -> MoodHistory:
        model = MoodHistoryModel(
            id=mood.id,
            character_id=mood.character_id,
            mood=mood.mood,
            trigger=mood.trigger,
            timestamp=mood.timestamp,
        )
        saved_model = await super().add(model)
        return self._to_domain(saved_model)

    async def delete(self, mood_id: uuid.UUID) -> None:
        async with self._uow() as uow:
            await uow.session.execute(
                delete(MoodHistoryModel).where(MoodHistoryModel.id == mood_id)
            )

    @staticmethod
    def _to_domain(model: MoodHistoryModel) -> MoodHistory:
        return MoodHistory(
            id=model.id,
            character_id=model.character_id,
            mood=model.mood,
            trigger=model.trigger,
            timestamp=model.timestamp,
        )
