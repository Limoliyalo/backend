from abc import ABC, abstractmethod

from src.domain.entities.user_pictures import UserPictures
from src.domain.value_objects.telegram_id import TelegramId


class UserPicturesRepository(ABC):
    @abstractmethod
    async def get(self, telegram_id: TelegramId) -> UserPictures:
        raise NotImplementedError

    @abstractmethod
    async def add_picture(
        self, telegram_id: TelegramId, picture_id: int
    ) -> UserPictures:
        raise NotImplementedError
