from collections.abc import Callable
import uuid
from datetime import datetime, timedelta

from sqlalchemy import delete, select

from src.adapters.database.models.activities import (
    ActivityTypeModel,
    BaseCharacterActivityModel,
    CharacterActivityHistoryModel,
    DailyProgressModel,
    FoodEntryModel,
    MoodHistoryModel,
)
from src.adapters.database.uow import AbstractUnitOfWork
from src.adapters.repositories.base import SQLAlchemyRepository
from src.domain.entities.healthity.activities import (
    ActivityType,
    BaseCharacterActivity,
    CharacterActivityHistory,
    DailyProgress,
    FoodEntry,
    MoodHistory,
)
from src.ports.repositories.healthity.activities import (
    ActivityTypesRepository,
    BaseCharacterActivitiesRepository,
    DailyActivitiesRepository,
    DailyProgressRepository,
    FoodEntriesRepository,
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

    async def get_by_id(self, activity_type_id: uuid.UUID) -> ActivityType | None:
        model = await super().get(activity_type_id)
        if model is None:
            return None
        return self._to_domain(model)

    async def add(self, activity_type: ActivityType) -> ActivityType:  # type: ignore[override]
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

    async def update(self, activity_type: ActivityType) -> ActivityType:
        async with self._uow() as uow:
            model = await uow.session.get(ActivityTypeModel, activity_type.id)
            if model is None:
                raise ValueError("ActivityType not found")

            model.name = activity_type.name
            model.unit = activity_type.unit
            model.color = activity_type.color
            model.daily_goal_default = activity_type.daily_goal_default

            await uow.session.flush()
            await uow.session.refresh(model)
            return self._to_domain(model)

    async def delete(self, activity_type_id: uuid.UUID) -> None:  # type: ignore[override]
        async with self._uow() as uow:
            await uow.session.execute(
                delete(ActivityTypeModel).where(
                    ActivityTypeModel.id == activity_type_id
                )
            )

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
    SQLAlchemyRepository[CharacterActivityHistoryModel], DailyActivitiesRepository
):
    model = CharacterActivityHistoryModel

    def __init__(self, uow_factory: Callable[[], AbstractUnitOfWork]) -> None:
        super().__init__(uow_factory)

    async def list_for_day(
        self, character_id: uuid.UUID, day: datetime
    ) -> list[CharacterActivityHistory]:
        models = await self.list(filters={"character_id": character_id, "date": day})
        return [self._to_domain(model) for model in models]

    async def list_for_date_range(
        self, character_id: uuid.UUID, start_date: datetime, end_date: datetime
    ) -> list[CharacterActivityHistory]:
        async with self._uow() as uow:
            result = await uow.session.execute(
                select(CharacterActivityHistoryModel)
                .where(
                    CharacterActivityHistoryModel.character_id == character_id,
                    CharacterActivityHistoryModel.date >= start_date,
                    CharacterActivityHistoryModel.date <= end_date,
                )
                .order_by(CharacterActivityHistoryModel.date.desc())
            )
            models = result.scalars().all()
        return [self._to_domain(model) for model in models]

    async def upsert(
        self, activity: CharacterActivityHistory
    ) -> CharacterActivityHistory:
        async with self._uow() as uow:
            model = await uow.session.get(CharacterActivityHistoryModel, activity.id)
            if model is None:
                model = CharacterActivityHistoryModel(
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

    async def get_by_id(
        self, activity_id: uuid.UUID
    ) -> CharacterActivityHistory | None:
        async with self._uow() as uow:
            model = await uow.session.get(CharacterActivityHistoryModel, activity_id)
            if model is None:
                return None
            return self._to_domain(model)

    async def update(
        self, activity: CharacterActivityHistory
    ) -> CharacterActivityHistory:
        async with self._uow() as uow:
            model = await uow.session.get(CharacterActivityHistoryModel, activity.id)
            if model is None:
                raise ValueError("CharacterActivityHistory not found")

            model.value = activity.value
            model.goal = activity.goal
            model.notes = activity.notes

            await uow.session.flush()
            await uow.session.refresh(model)
            return self._to_domain(model)

    async def delete(self, activity_id: uuid.UUID) -> None:  # type: ignore[override]
        async with self._uow() as uow:
            from sqlalchemy import delete as sql_delete

            await uow.session.execute(
                sql_delete(CharacterActivityHistoryModel).where(
                    CharacterActivityHistoryModel.id == activity_id
                )
            )

    async def get_by_character_activity_date(
        self, character_id: uuid.UUID, activity_type_id: uuid.UUID, date: datetime
    ) -> CharacterActivityHistory | None:
        model = await self.first(
            filters={
                "character_id": character_id,
                "activity_type_id": activity_type_id,
                "date": date,
            }
        )
        if model is None:
            return None
        return self._to_domain(model)

    @staticmethod
    def _to_domain(model: CharacterActivityHistoryModel) -> CharacterActivityHistory:
        return CharacterActivityHistory(
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


class SQLAlchemyFoodEntriesRepository(
    SQLAlchemyRepository[FoodEntryModel], FoodEntriesRepository
):
    model = FoodEntryModel

    def __init__(self, uow_factory: Callable[[], AbstractUnitOfWork]) -> None:
        super().__init__(uow_factory)

    async def list_for_day(
        self, character_id: uuid.UUID, day: datetime
    ) -> list[FoodEntry]:
        normalized_day = day
        if normalized_day.tzinfo is not None:
            normalized_day = normalized_day.replace(tzinfo=None)
        day_start = normalized_day.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)

        async with self._uow() as uow:
            result = await uow.session.execute(
                select(FoodEntryModel)
                .where(
                    FoodEntryModel.character_id == character_id,
                    FoodEntryModel.consumed_at >= day_start,
                    FoodEntryModel.consumed_at < day_end,
                )
                .order_by(FoodEntryModel.consumed_at.desc())
            )
            models = result.scalars().all()
        return [self._to_domain(model) for model in models]

    async def get_by_id(self, entry_id: uuid.UUID) -> FoodEntry | None:
        async with self._uow() as uow:
            model = await uow.session.get(FoodEntryModel, entry_id)
            if model is None:
                return None
            return self._to_domain(model)

    async def add(self, entry: FoodEntry) -> FoodEntry:  # type: ignore[override]
        model = FoodEntryModel(
            id=entry.id,
            character_id=entry.character_id,
            consumed_at=entry.consumed_at,
            meal_type=entry.meal_type,
            title=entry.title,
            calories=entry.calories,
            protein_g=entry.protein_g,
            fat_g=entry.fat_g,
            carbs_g=entry.carbs_g,
            notes=entry.notes,
            created_at=entry.created_at,
            updated_at=entry.updated_at,
        )
        saved_model = await super().add(model)
        return self._to_domain(saved_model)

    async def update(self, entry: FoodEntry) -> FoodEntry:
        async with self._uow() as uow:
            model = await uow.session.get(FoodEntryModel, entry.id)
            if model is None:
                raise ValueError("FoodEntry not found")

            model.consumed_at = entry.consumed_at
            model.meal_type = entry.meal_type
            model.title = entry.title
            model.calories = entry.calories
            model.protein_g = entry.protein_g
            model.fat_g = entry.fat_g
            model.carbs_g = entry.carbs_g
            model.notes = entry.notes

            await uow.session.flush()
            await uow.session.refresh(model)
            return self._to_domain(model)

    async def delete(self, entry_id: uuid.UUID) -> None:  # type: ignore[override]
        async with self._uow() as uow:
            await uow.session.execute(
                delete(FoodEntryModel).where(FoodEntryModel.id == entry_id)
            )

    @staticmethod
    def _to_domain(model: FoodEntryModel) -> FoodEntry:
        return FoodEntry(
            id=model.id,
            character_id=model.character_id,
            consumed_at=model.consumed_at,
            meal_type=model.meal_type,
            title=model.title,
            calories=model.calories,
            protein_g=model.protein_g,
            fat_g=model.fat_g,
            carbs_g=model.carbs_g,
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

    async def list_for_date_range(
        self, character_id: uuid.UUID, start_date: datetime, end_date: datetime
    ) -> list[DailyProgress]:
        async with self._uow() as uow:
            result = await uow.session.execute(
                select(DailyProgressModel)
                .where(
                    DailyProgressModel.character_id == character_id,
                    DailyProgressModel.date >= start_date,
                    DailyProgressModel.date <= end_date,
                )
                .order_by(DailyProgressModel.date.desc())
            )
            models = result.scalars().all()
        return [self._to_domain(model) for model in models]

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

    async def list_for_character(self, character_id: uuid.UUID) -> list[DailyProgress]:
        models = await self.list(filters={"character_id": character_id})
        return [self._to_domain(model) for model in models]

    async def get_by_id(self, progress_id: uuid.UUID) -> DailyProgress | None:
        async with self._uow() as uow:
            model = await uow.session.get(DailyProgressModel, progress_id)
            if model is None:
                return None
            return self._to_domain(model)

    async def update(self, progress: DailyProgress) -> DailyProgress:
        async with self._uow() as uow:
            model = await uow.session.get(DailyProgressModel, progress.id)
            if model is None:
                raise ValueError("DailyProgress not found")

            model.experience_gained = progress.experience_gained
            model.level_at_end = progress.level_at_end
            model.mood_average = progress.mood_average
            model.behavior_index = progress.behavior_index

            await uow.session.flush()
            await uow.session.refresh(model)
            return self._to_domain(model)

    async def delete(self, progress_id: uuid.UUID) -> None:  # type: ignore[override]
        async with self._uow() as uow:
            from sqlalchemy import delete as sql_delete

            await uow.session.execute(
                sql_delete(DailyProgressModel).where(
                    DailyProgressModel.id == progress_id
                )
            )

    async def get_by_character_date(
        self, character_id: uuid.UUID, date: datetime
    ) -> DailyProgress | None:
        model = await self.first(filters={"character_id": character_id, "date": date})
        if model is None:
            return None
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

    async def list_for_date_range(
        self, character_id: uuid.UUID, start_date: datetime, end_date: datetime
    ) -> list[MoodHistory]:
        async with self._uow() as uow:
            result = await uow.session.execute(
                select(MoodHistoryModel)
                .where(
                    MoodHistoryModel.character_id == character_id,
                    MoodHistoryModel.timestamp >= start_date,
                    MoodHistoryModel.timestamp <= end_date,
                )
                .order_by(MoodHistoryModel.timestamp.desc())
            )
            models = result.scalars().all()
        return [self._to_domain(model) for model in models]

    async def get_by_id(self, mood_id: uuid.UUID) -> MoodHistory | None:
        model = await self.first(filters={"id": mood_id})
        if model is None:
            return None
        return self._to_domain(model)

    async def add(self, mood: MoodHistory) -> MoodHistory:  # type: ignore[override]
        model = MoodHistoryModel(
            id=mood.id,
            character_id=mood.character_id,
            mood=mood.mood,
            trigger=mood.trigger,
            timestamp=mood.timestamp,
        )
        saved_model = await super().add(model)
        return self._to_domain(saved_model)

    async def update(self, mood: MoodHistory) -> MoodHistory:
        async with self._uow() as uow:
            model = await uow.session.get(MoodHistoryModel, mood.id)
            if model is None:
                raise ValueError("MoodHistory not found")

            model.mood = mood.mood
            model.trigger = mood.trigger

            await uow.session.flush()
            await uow.session.refresh(model)
            return self._to_domain(model)

    async def delete(self, mood_id: uuid.UUID) -> None:  # type: ignore[override]
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


class SQLAlchemyBaseCharacterActivitiesRepository(
    SQLAlchemyRepository[BaseCharacterActivityModel], BaseCharacterActivitiesRepository
):
    model = BaseCharacterActivityModel

    def __init__(self, uow_factory: Callable[[], AbstractUnitOfWork]) -> None:
        super().__init__(uow_factory)

    async def list_for_character(
        self, character_id: uuid.UUID
    ) -> list[BaseCharacterActivity]:
        models = await self.list(filters={"character_id": character_id})
        return [self._to_domain(model) for model in models]

    async def get_by_id(self, activity_id: uuid.UUID) -> BaseCharacterActivity | None:
        model = await super().get(activity_id)
        if model is None:
            return None
        return self._to_domain(model)

    async def get_by_character_and_type(
        self, character_id: uuid.UUID, activity_type_id: uuid.UUID
    ) -> BaseCharacterActivity | None:
        model = await self.first(
            filters={
                "character_id": character_id,
                "activity_type_id": activity_type_id,
            }
        )
        if model is None:
            return None
        return self._to_domain(model)

    async def add(self, activity: BaseCharacterActivity) -> BaseCharacterActivity:  # type: ignore[override]
        model = BaseCharacterActivityModel(
            id=activity.id,
            character_id=activity.character_id,
            activity_type_id=activity.activity_type_id,
            goal=activity.goal,
            created_at=activity.created_at,
            updated_at=activity.updated_at,
        )
        saved_model = await super().add(model)
        return self._to_domain(saved_model)

    async def update(self, activity: BaseCharacterActivity) -> BaseCharacterActivity:
        async with self._uow() as uow:
            model = await uow.session.get(BaseCharacterActivityModel, activity.id)
            if model is None:
                raise ValueError("BaseCharacterActivity not found")

            model.goal = activity.goal

            await uow.session.flush()
            await uow.session.refresh(model)
            return self._to_domain(model)

    async def delete(self, activity_id: uuid.UUID) -> None:  # type: ignore[override]
        async with self._uow() as uow:
            from sqlalchemy import delete as sql_delete

            await uow.session.execute(
                sql_delete(BaseCharacterActivityModel).where(
                    BaseCharacterActivityModel.id == activity_id
                )
            )

    @staticmethod
    def _to_domain(model: BaseCharacterActivityModel) -> BaseCharacterActivity:
        return BaseCharacterActivity(
            id=model.id,
            character_id=model.character_id,
            activity_type_id=model.activity_type_id,
            goal=model.goal,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
