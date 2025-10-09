from abc import ABC, abstractmethod

from src.domain.entities.picture import Picture
from src.domain.value_objects.telegram_id import TelegramId


class PicturesRepository(ABC):
    @abstractmethod
    async def create(self, picture: Picture) -> Picture:
        raise NotImplementedError

    @abstractmethod
    async def get_by_owner(self, telegram_id: TelegramId) -> Picture | None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(
        self, picture_id: int, telegram_id: TelegramId
    ) -> Picture | None:
        raise NotImplementedError

    @abstractmethod
    async def mark_opened(self, picture_id: int, telegram_id: TelegramId) -> None:
        raise NotImplementedError

    @abstractmethod
    async def update(self, picture: Picture) -> Picture:
        raise NotImplementedError
