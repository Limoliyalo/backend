import uuid
from dataclasses import dataclass, field
from datetime import datetime

from src.domain.entities.healthity.activities import (
    CharacterActivityHistory,
    FoodEntry,
)
from src.domain.exceptions import EntityNotFoundException
from src.ports.repositories.healthity.activities import (
    ActivityTypesRepository,
    BaseCharacterActivitiesRepository,
    DailyActivitiesRepository,
    FoodEntriesRepository,
)


@dataclass
class FoodEntrySummary:
    total_calories: int
    total_protein_g: int
    total_fat_g: int
    total_carbs_g: int
    last_entry_at: datetime | None


@dataclass
class FoodEntriesForDay:
    entries: list[FoodEntry]
    summary: FoodEntrySummary


@dataclass
class CreateFoodEntryInput:
    character_id: uuid.UUID
    consumed_at: datetime
    meal_type: str
    title: str | None
    calories: int
    protein_g: int | None = None
    fat_g: int | None = None
    carbs_g: int | None = None
    notes: str | None = None


@dataclass
class UpdateFoodEntryInput:
    entry_id: uuid.UUID
    character_id: uuid.UUID
    consumed_at: datetime | None = None
    meal_type: str | None = None
    title: str | None = None
    calories: int | None = None
    protein_g: int | None = None
    fat_g: int | None = None
    carbs_g: int | None = None
    notes: str | None = None
    fields_to_update: set[str] = field(default_factory=set)


def _normalize_datetime(value: datetime) -> datetime:
    if value.tzinfo is not None:
        return value.replace(tzinfo=None)
    return value


def _normalize_day(value: datetime) -> datetime:
    normalized = _normalize_datetime(value)
    return normalized.replace(hour=0, minute=0, second=0, microsecond=0)


def _build_summary(entries: list[FoodEntry]) -> FoodEntrySummary:
    return FoodEntrySummary(
        total_calories=sum(entry.calories for entry in entries),
        total_protein_g=sum(entry.protein_g or 0 for entry in entries),
        total_fat_g=sum(entry.fat_g or 0 for entry in entries),
        total_carbs_g=sum(entry.carbs_g or 0 for entry in entries),
        last_entry_at=max((entry.consumed_at for entry in entries), default=None),
    )


class FoodDailyActivitySync:
    def __init__(
        self,
        daily_activities_repository: DailyActivitiesRepository,
        base_activities_repository: BaseCharacterActivitiesRepository,
        activity_types_repository: ActivityTypesRepository,
        food_entries_repository: FoodEntriesRepository,
    ) -> None:
        self._daily_activities_repository = daily_activities_repository
        self._base_activities_repository = base_activities_repository
        self._activity_types_repository = activity_types_repository
        self._food_entries_repository = food_entries_repository

    async def sync_day(self, character_id: uuid.UUID, day: datetime) -> datetime:
        food_type = await self._activity_types_repository.get_by_name("food")
        if food_type is None:
            raise EntityNotFoundException("Activity type food not found")

        base_activity = (
            await self._base_activities_repository.get_by_character_and_type(
                character_id, food_type.id
            )
        )
        if base_activity is None:
            raise EntityNotFoundException(
                "Food activity is not in character's base activities"
            )

        date_only = _normalize_day(day)
        entries = await self._food_entries_repository.list_for_day(
            character_id, date_only
        )
        total_calories = sum(entry.calories for entry in entries)
        existing_activity = (
            await self._daily_activities_repository.get_by_character_activity_date(
                character_id, food_type.id, date_only
            )
        )

        if existing_activity is not None:
            existing_activity.value = total_calories
            existing_activity.goal = base_activity.goal
            existing_activity.touch()
            await self._daily_activities_repository.update(existing_activity)
            return date_only

        if total_calories > 0:
            activity = CharacterActivityHistory(
                id=uuid.uuid4(),
                character_id=character_id,
                activity_type_id=food_type.id,
                date=date_only,
                value=total_calories,
                goal=base_activity.goal,
                notes=None,
            )
            await self._daily_activities_repository.upsert(activity)

        return date_only


class ListFoodEntriesForDayUseCase:
    def __init__(self, food_entries_repository: FoodEntriesRepository) -> None:
        self._food_entries_repository = food_entries_repository

    async def execute(self, character_id: uuid.UUID, day: datetime) -> FoodEntriesForDay:
        entries = await self._food_entries_repository.list_for_day(
            character_id, _normalize_day(day)
        )
        return FoodEntriesForDay(entries=entries, summary=_build_summary(entries))


class CreateFoodEntryUseCase:
    def __init__(
        self,
        food_entries_repository: FoodEntriesRepository,
        daily_activities_repository: DailyActivitiesRepository,
        base_activities_repository: BaseCharacterActivitiesRepository,
        activity_types_repository: ActivityTypesRepository,
    ) -> None:
        self._food_entries_repository = food_entries_repository
        self._sync = FoodDailyActivitySync(
            daily_activities_repository=daily_activities_repository,
            base_activities_repository=base_activities_repository,
            activity_types_repository=activity_types_repository,
            food_entries_repository=food_entries_repository,
        )

    async def execute(self, data: CreateFoodEntryInput) -> FoodEntry:
        consumed_at = _normalize_datetime(data.consumed_at)
        entry = FoodEntry(
            id=uuid.uuid4(),
            character_id=data.character_id,
            consumed_at=consumed_at,
            meal_type=data.meal_type,
            title=data.title,
            calories=data.calories,
            protein_g=data.protein_g,
            fat_g=data.fat_g,
            carbs_g=data.carbs_g,
            notes=data.notes,
        )
        saved_entry = await self._food_entries_repository.add(entry)
        await self._sync.sync_day(data.character_id, consumed_at)
        return saved_entry


class UpdateFoodEntryUseCase:
    def __init__(
        self,
        food_entries_repository: FoodEntriesRepository,
        daily_activities_repository: DailyActivitiesRepository,
        base_activities_repository: BaseCharacterActivitiesRepository,
        activity_types_repository: ActivityTypesRepository,
    ) -> None:
        self._food_entries_repository = food_entries_repository
        self._sync = FoodDailyActivitySync(
            daily_activities_repository=daily_activities_repository,
            base_activities_repository=base_activities_repository,
            activity_types_repository=activity_types_repository,
            food_entries_repository=food_entries_repository,
        )

    async def execute(self, data: UpdateFoodEntryInput) -> FoodEntry:
        entry = await self._food_entries_repository.get_by_id(data.entry_id)
        if entry is None or entry.character_id != data.character_id:
            raise EntityNotFoundException(f"FoodEntry {data.entry_id} not found")

        original_day = _normalize_day(entry.consumed_at)
        fields = data.fields_to_update or {
            name
            for name in (
                "consumed_at",
                "meal_type",
                "title",
                "calories",
                "protein_g",
                "fat_g",
                "carbs_g",
                "notes",
            )
            if getattr(data, name) is not None
        }

        if "consumed_at" in fields and data.consumed_at is not None:
            entry.consumed_at = _normalize_datetime(data.consumed_at)
        if "meal_type" in fields and data.meal_type is not None:
            entry.meal_type = data.meal_type
        if "title" in fields:
            entry.title = data.title
        if "calories" in fields and data.calories is not None:
            entry.calories = data.calories
        if "protein_g" in fields:
            entry.protein_g = data.protein_g
        if "fat_g" in fields:
            entry.fat_g = data.fat_g
        if "carbs_g" in fields:
            entry.carbs_g = data.carbs_g
        if "notes" in fields:
            entry.notes = data.notes

        entry.touch()
        saved_entry = await self._food_entries_repository.update(entry)
        await self._sync.sync_day(data.character_id, original_day)
        if _normalize_day(saved_entry.consumed_at) != original_day:
            await self._sync.sync_day(data.character_id, saved_entry.consumed_at)
        return saved_entry


class DeleteFoodEntryUseCase:
    def __init__(
        self,
        food_entries_repository: FoodEntriesRepository,
        daily_activities_repository: DailyActivitiesRepository,
        base_activities_repository: BaseCharacterActivitiesRepository,
        activity_types_repository: ActivityTypesRepository,
    ) -> None:
        self._food_entries_repository = food_entries_repository
        self._sync = FoodDailyActivitySync(
            daily_activities_repository=daily_activities_repository,
            base_activities_repository=base_activities_repository,
            activity_types_repository=activity_types_repository,
            food_entries_repository=food_entries_repository,
        )

    async def execute(self, entry_id: uuid.UUID, character_id: uuid.UUID) -> datetime:
        entry = await self._food_entries_repository.get_by_id(entry_id)
        if entry is None or entry.character_id != character_id:
            raise EntityNotFoundException(f"FoodEntry {entry_id} not found")

        sync_day = _normalize_day(entry.consumed_at)
        await self._food_entries_repository.delete(entry_id)
        await self._sync.sync_day(character_id, sync_day)
        return sync_day
