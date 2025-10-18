from abc import ABC, abstractmethod

from src.domain.entities.healthity.users import User, UserFriend, UserSettings
from src.domain.value_objects.telegram_id import TelegramId


class UserSettingsRepository(ABC):
    @abstractmethod
    async def get_by_user(self, user_tg_id: TelegramId) -> UserSettings | None:
        raise NotImplementedError

    @abstractmethod
    async def upsert(self, settings: UserSettings) -> UserSettings:
        raise NotImplementedError


class UserFriendsRepository(ABC):
    @abstractmethod
    async def list_for_user(self, owner_tg_id: TelegramId) -> list[UserFriend]:
        raise NotImplementedError

    @abstractmethod
    async def add(self, friend: UserFriend) -> UserFriend:
        raise NotImplementedError

    @abstractmethod
    async def remove(self, owner_tg_id: TelegramId, friend_tg_id: TelegramId) -> None:
        raise NotImplementedError


class UsersRepository(ABC):
    @abstractmethod
    async def create(self, user: User) -> User:
        raise NotImplementedError

    @abstractmethod
    async def get_by_telegram_id(self, telegram_id: TelegramId) -> User | None:
        raise NotImplementedError

    @abstractmethod
    async def update(self, user: User) -> User:
        raise NotImplementedError

    @abstractmethod
    async def list_all(self, limit: int = 100, offset: int = 0) -> list[User]:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, telegram_id: TelegramId) -> None:
        raise NotImplementedError
