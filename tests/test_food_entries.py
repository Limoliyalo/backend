import asyncio
import uuid
from datetime import datetime, timedelta

import pytest
from pydantic import ValidationError

from src.domain.entities.healthity.activities import (
    ActivityType,
    BaseCharacterActivity,
    CharacterActivityHistory,
    FoodEntry,
)
from src.domain.exceptions import EntityNotFoundException
from src.drivers.rest.food_entries import create_my_food_entry
from src.drivers.rest.schemas.food_entries import FoodEntryCreate, FoodEntryUpdate
from src.use_cases.food_entries.manage_food_entries import (
    CreateFoodEntryInput,
    CreateFoodEntryUseCase,
    DeleteFoodEntryUseCase,
    ListFoodEntriesForDayUseCase,
    UpdateFoodEntryInput,
    UpdateFoodEntryUseCase,
)


class StaticActivityTypesRepository:
    def __init__(self, food_type: ActivityType) -> None:
        self.food_type = food_type

    async def get_by_name(self, name: str):
        return self.food_type if name == "food" else None

    async def get_by_id(self, activity_type_id: uuid.UUID):
        return self.food_type if activity_type_id == self.food_type.id else None


class StaticBaseActivitiesRepository:
    def __init__(self, base_activity: BaseCharacterActivity | None) -> None:
        self.base_activity = base_activity

    async def get_by_character_and_type(
        self, character_id: uuid.UUID, activity_type_id: uuid.UUID
    ):
        if (
            self.base_activity
            and self.base_activity.character_id == character_id
            and self.base_activity.activity_type_id == activity_type_id
        ):
            return self.base_activity
        return None


class MemoryDailyActivitiesRepository:
    def __init__(self) -> None:
        self.activities: dict[tuple[uuid.UUID, uuid.UUID, datetime], CharacterActivityHistory] = {}
        self.upserts = 0
        self.updates = 0

    async def list_for_day(self, character_id: uuid.UUID, day: datetime):
        return [
            activity
            for (stored_character_id, _activity_type_id, stored_day), activity in self.activities.items()
            if stored_character_id == character_id and stored_day == day
        ]

    async def get_by_character_activity_date(
        self, character_id: uuid.UUID, activity_type_id: uuid.UUID, date: datetime
    ):
        return self.activities.get((character_id, activity_type_id, date))

    async def upsert(self, activity: CharacterActivityHistory):
        self.upserts += 1
        self.activities[(activity.character_id, activity.activity_type_id, activity.date)] = activity
        return activity

    async def update(self, activity: CharacterActivityHistory):
        self.updates += 1
        self.activities[(activity.character_id, activity.activity_type_id, activity.date)] = activity
        return activity


class MemoryFoodEntriesRepository:
    def __init__(self) -> None:
        self.entries: dict[uuid.UUID, FoodEntry] = {}

    async def list_for_day(self, character_id: uuid.UUID, day: datetime):
        next_day = day + timedelta(days=1)
        return sorted(
            [
                entry
                for entry in self.entries.values()
                if entry.character_id == character_id
                and day <= entry.consumed_at < next_day
            ],
            key=lambda entry: entry.consumed_at,
            reverse=True,
        )

    async def get_by_id(self, entry_id: uuid.UUID):
        return self.entries.get(entry_id)

    async def add(self, entry: FoodEntry):
        self.entries[entry.id] = entry
        return entry

    async def update(self, entry: FoodEntry):
        self.entries[entry.id] = entry
        return entry

    async def delete(self, entry_id: uuid.UUID):
        self.entries.pop(entry_id, None)


def test_food_entry_schema_trims_optional_text_and_validates_limits() -> None:
    payload = FoodEntryCreate(
        consumed_at=datetime(2026, 6, 5, 9, 30),
        meal_type="breakfast",
        title="  Омлет  ",
        calories=420,
        protein_g=20,
        fat_g=15,
        carbs_g=5,
        notes="   ",
    )

    assert payload.title == "Омлет"
    assert payload.notes is None

    FoodEntryCreate(
        consumed_at=datetime(2026, 6, 5, 9, 30),
        meal_type="snack",
        title="a" * 100,
        calories=1,
    )

    with pytest.raises(ValidationError):
        FoodEntryCreate(
            consumed_at=datetime(2026, 6, 5, 9, 30),
            meal_type="other",
            title="a" * 101,
            calories=1,
        )

    with pytest.raises(ValidationError):
        FoodEntryUpdate(entry_id=uuid.uuid4(), calories=0)

    with pytest.raises(ValidationError):
        FoodEntryUpdate(entry_id=uuid.uuid4(), protein_g=-1)


def test_food_entries_summary_uses_latest_consumed_at_and_empty_day_has_no_last_entry() -> None:
    character_id = uuid.uuid4()
    food_type_id = uuid.uuid4()
    repos = make_repositories(character_id, food_type_id)
    entries_repo = repos["entries"]

    async def run() -> None:
        entries_repo.entries[uuid.uuid4()] = FoodEntry(
            id=uuid.uuid4(),
            character_id=character_id,
            consumed_at=datetime(2026, 6, 5, 8, 0),
            meal_type="breakfast",
            title="Каша",
            calories=300,
        )
        entries_repo.entries[uuid.uuid4()] = FoodEntry(
            id=uuid.uuid4(),
            character_id=character_id,
            consumed_at=datetime(2026, 6, 5, 13, 15),
            meal_type="lunch",
            title="Суп",
            calories=500,
        )

        use_case = ListFoodEntriesForDayUseCase(entries_repo)
        result = await use_case.execute(character_id, datetime(2026, 6, 5, 21, 0))
        empty = await use_case.execute(character_id, datetime(2026, 6, 6, 21, 0))

        assert result.summary.total_calories == 800
        assert result.summary.last_entry_at == datetime(2026, 6, 5, 13, 15)
        assert empty.summary.total_calories == 0
        assert empty.summary.last_entry_at is None

    asyncio.run(run())


def test_food_entry_create_update_delete_recomputes_daily_food_progress_without_double_counting() -> None:
    character_id = uuid.uuid4()
    food_type_id = uuid.uuid4()
    repos = make_repositories(character_id, food_type_id)

    create_use_case = CreateFoodEntryUseCase(
        food_entries_repository=repos["entries"],
        daily_activities_repository=repos["daily"],
        base_activities_repository=repos["base"],
        activity_types_repository=repos["types"],
    )
    update_use_case = UpdateFoodEntryUseCase(
        food_entries_repository=repos["entries"],
        daily_activities_repository=repos["daily"],
        base_activities_repository=repos["base"],
        activity_types_repository=repos["types"],
    )
    delete_use_case = DeleteFoodEntryUseCase(
        food_entries_repository=repos["entries"],
        daily_activities_repository=repos["daily"],
        base_activities_repository=repos["base"],
        activity_types_repository=repos["types"],
    )

    async def run() -> None:
        first = await create_use_case.execute(
            CreateFoodEntryInput(
                character_id=character_id,
                consumed_at=datetime(2026, 6, 5, 8, 30),
                meal_type="breakfast",
                title="Каша",
                calories=450,
            )
        )
        second = await create_use_case.execute(
            CreateFoodEntryInput(
                character_id=character_id,
                consumed_at=datetime(2026, 6, 5, 13, 0),
                meal_type="lunch",
                title="Суп",
                calories=300,
            )
        )

        daily = repos["daily"].activities[
            (character_id, food_type_id, datetime(2026, 6, 5))
        ]
        assert daily.value == 750
        assert daily.goal == 2000

        await update_use_case.execute(
            UpdateFoodEntryInput(
                entry_id=first.id,
                character_id=character_id,
                calories=500,
            )
        )
        assert daily.value == 800

        await delete_use_case.execute(second.id, character_id)
        assert daily.value == 500
        assert repos["daily"].upserts == 1
        assert repos["daily"].updates == 3

    asyncio.run(run())


def test_food_entry_update_rejects_entries_owned_by_another_character() -> None:
    character_id = uuid.uuid4()
    owner_id = uuid.uuid4()
    food_type_id = uuid.uuid4()
    repos = make_repositories(character_id, food_type_id)
    entry_id = uuid.uuid4()
    repos["entries"].entries[entry_id] = FoodEntry(
        id=entry_id,
        character_id=owner_id,
        consumed_at=datetime(2026, 6, 5, 8, 30),
        meal_type="breakfast",
        title="Каша",
        calories=450,
    )
    use_case = UpdateFoodEntryUseCase(
        food_entries_repository=repos["entries"],
        daily_activities_repository=repos["daily"],
        base_activities_repository=repos["base"],
        activity_types_repository=repos["types"],
    )

    async def run() -> None:
        with pytest.raises(EntityNotFoundException):
            await use_case.execute(
                UpdateFoodEntryInput(
                    entry_id=entry_id,
                    character_id=character_id,
                    calories=500,
                )
            )

    asyncio.run(run())


def test_create_food_entry_route_recalculates_xp_for_synced_day() -> None:
    character_id = uuid.uuid4()
    entry = FoodEntry(
        id=uuid.uuid4(),
        character_id=character_id,
        consumed_at=datetime(2026, 6, 5, 8, 30),
        meal_type="breakfast",
        title="Каша",
        calories=450,
    )
    recalculate_calls = []

    class StaticCharacterUseCase:
        async def execute(self, telegram_id: int):
            return type("Character", (), {"id": character_id})()

    class StaticCreateUseCase:
        async def execute(self, data):
            return entry

    class RecordingRecalculateXpUseCase:
        async def execute(self, data):
            recalculate_calls.append(data)

    async def run() -> None:
        await create_my_food_entry(
            FoodEntryCreate(
                consumed_at=entry.consumed_at,
                meal_type="breakfast",
                title=entry.title,
                calories=entry.calories,
            ),
            telegram_id=123,
            get_character_use_case=StaticCharacterUseCase(),
            use_case=StaticCreateUseCase(),
            recalculate_xp_use_case=RecordingRecalculateXpUseCase(),
        )

    asyncio.run(run())

    assert len(recalculate_calls) == 1
    assert recalculate_calls[0].character_id == character_id
    assert recalculate_calls[0].date == entry.consumed_at


def make_repositories(character_id: uuid.UUID, food_type_id: uuid.UUID):
    food_type = ActivityType(
        id=food_type_id,
        name="food",
        unit="kcal",
        color="#4CAF50",
        daily_goal_default=2000,
    )
    base_activity = BaseCharacterActivity(
        id=uuid.uuid4(),
        character_id=character_id,
        activity_type_id=food_type_id,
        goal=2000,
    )
    return {
        "types": StaticActivityTypesRepository(food_type),
        "base": StaticBaseActivitiesRepository(base_activity),
        "daily": MemoryDailyActivitiesRepository(),
        "entries": MemoryFoodEntriesRepository(),
    }
