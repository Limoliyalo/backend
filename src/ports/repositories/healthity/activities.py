from abc import ABC, abstractmethod
import uuid
from datetime import datetime

from src.domain.entities.healthity.activities import (
    ActivityType,
    BaseCharacterActivity,
    CharacterActivityHistory,
    DailyProgress,
    FoodEntry,
    MoodHistory,
)


class ActivityTypesRepository(ABC):
    @abstractmethod
    async def list_all(self) -> list[ActivityType]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_name(self, name: str) -> ActivityType | None:
        raise NotImplementedError

    @abstractmethod
    async def add(self, activity_type: ActivityType) -> ActivityType:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, activity_type_id: uuid.UUID) -> ActivityType | None:
        raise NotImplementedError

    @abstractmethod
    async def update(self, activity_type: ActivityType) -> ActivityType:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, activity_type_id: uuid.UUID) -> None:
        raise NotImplementedError


class DailyActivitiesRepository(ABC):
    @abstractmethod
    async def list_for_day(
        self, character_id: uuid.UUID, day: datetime
    ) -> list[CharacterActivityHistory]:
        raise NotImplementedError

    @abstractmethod
    async def list_for_date_range(
        self, character_id: uuid.UUID, start_date: datetime, end_date: datetime
    ) -> list[CharacterActivityHistory]:
        raise NotImplementedError

    @abstractmethod
    async def upsert(
        self, activity: CharacterActivityHistory
    ) -> CharacterActivityHistory:
        raise NotImplementedError

    @abstractmethod
    async def get_by_character_activity_date(
        self, character_id: uuid.UUID, activity_type_id: uuid.UUID, date: datetime
    ) -> CharacterActivityHistory | None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(
        self, activity_id: uuid.UUID
    ) -> CharacterActivityHistory | None:
        raise NotImplementedError

    @abstractmethod
    async def update(
        self, activity: CharacterActivityHistory
    ) -> CharacterActivityHistory:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, activity_id: uuid.UUID) -> None:
        raise NotImplementedError


class FoodEntriesRepository(ABC):
    @abstractmethod
    async def list_for_day(
        self, character_id: uuid.UUID, day: datetime
    ) -> list[FoodEntry]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, entry_id: uuid.UUID) -> FoodEntry | None:
        raise NotImplementedError

    @abstractmethod
    async def add(self, entry: FoodEntry) -> FoodEntry:
        raise NotImplementedError

    @abstractmethod
    async def update(self, entry: FoodEntry) -> FoodEntry:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, entry_id: uuid.UUID) -> None:
        raise NotImplementedError


class BaseCharacterActivitiesRepository(ABC):
    @abstractmethod
    async def list_for_character(
        self, character_id: uuid.UUID
    ) -> list[BaseCharacterActivity]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, activity_id: uuid.UUID) -> BaseCharacterActivity | None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_character_and_type(
        self, character_id: uuid.UUID, activity_type_id: uuid.UUID
    ) -> BaseCharacterActivity | None:
        raise NotImplementedError

    @abstractmethod
    async def add(self, activity: BaseCharacterActivity) -> BaseCharacterActivity:
        raise NotImplementedError

    @abstractmethod
    async def update(self, activity: BaseCharacterActivity) -> BaseCharacterActivity:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, activity_id: uuid.UUID) -> None:
        raise NotImplementedError


class DailyProgressRepository(ABC):
    @abstractmethod
    async def get_for_day(
        self, character_id: uuid.UUID, day: datetime
    ) -> DailyProgress | None:
        raise NotImplementedError

    @abstractmethod
    async def list_for_date_range(
        self, character_id: uuid.UUID, start_date: datetime, end_date: datetime
    ) -> list[DailyProgress]:
        raise NotImplementedError

    @abstractmethod
    async def upsert(self, progress: DailyProgress) -> DailyProgress:
        raise NotImplementedError

    @abstractmethod
    async def get_by_character_date(
        self, character_id: uuid.UUID, date: datetime
    ) -> DailyProgress | None:
        raise NotImplementedError

    @abstractmethod
    async def update(self, progress: DailyProgress) -> DailyProgress:
        raise NotImplementedError

    @abstractmethod
    async def list_for_character(self, character_id: uuid.UUID) -> list[DailyProgress]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, progress_id: uuid.UUID) -> DailyProgress | None:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, progress_id: uuid.UUID) -> None:
        raise NotImplementedError


class MoodHistoryRepository(ABC):
    @abstractmethod
    async def list_recent(
        self, character_id: uuid.UUID, limit: int = 20
    ) -> list[MoodHistory]:
        raise NotImplementedError

    @abstractmethod
    async def list_for_character(
        self, character_id: uuid.UUID, limit: int = 100
    ) -> list[MoodHistory]:
        raise NotImplementedError

    @abstractmethod
    async def list_for_date_range(
        self, character_id: uuid.UUID, start_date: datetime, end_date: datetime
    ) -> list[MoodHistory]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, mood_id: uuid.UUID) -> MoodHistory | None:
        raise NotImplementedError

    @abstractmethod
    async def add(self, mood: MoodHistory) -> MoodHistory:
        raise NotImplementedError

    @abstractmethod
    async def update(self, mood: MoodHistory) -> MoodHistory:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, mood_id: uuid.UUID) -> None:
        raise NotImplementedError
