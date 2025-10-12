from abc import ABC, abstractmethod
import uuid
from datetime import datetime

from src.domain.entities.healthity.activities import (
    ActivityType,
    DailyActivity,
    DailyProgress,
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


class DailyActivitiesRepository(ABC):
    @abstractmethod
    async def list_for_day(
        self, character_id: uuid.UUID, day: datetime
    ) -> list[DailyActivity]:
        raise NotImplementedError

    @abstractmethod
    async def list_for_date_range(
        self, character_id: uuid.UUID, start_date: datetime, end_date: datetime
    ) -> list[DailyActivity]:
        raise NotImplementedError

    @abstractmethod
    async def upsert(self, activity: DailyActivity) -> DailyActivity:
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
    async def delete(self, mood_id: uuid.UUID) -> None:
        raise NotImplementedError
