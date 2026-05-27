from abc import ABC, abstractmethod
import uuid

from src.domain.entities.healthity.users import User, UserFriend, UserSettings


class UserSettingsRepository(ABC):
    @abstractmethod
    async def get_by_user(self, user_tg_id: int) -> UserSettings | None:
        raise NotImplementedError

    @abstractmethod
    async def upsert(self, settings: UserSettings) -> UserSettings:
        raise NotImplementedError

    @abstractmethod
    async def list_all(self) -> list[UserSettings]:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, settings_id: uuid.UUID) -> None:
        raise NotImplementedError


class UserFriendsRepository(ABC):
    @abstractmethod
    async def list_for_user(self, owner_tg_id: int) -> list[UserFriend]:
        raise NotImplementedError

    @abstractmethod
    async def list_incoming_pending(self, user_tg_id: int) -> list[UserFriend]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_pair(
        self, owner_tg_id: int, friend_tg_id: int
    ) -> UserFriend | None:
        raise NotImplementedError

    @abstractmethod
    async def exists_pair(self, owner_tg_id: int, friend_tg_id: int) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def add(self, friend: UserFriend) -> UserFriend:
        raise NotImplementedError

    @abstractmethod
    async def remove(self, owner_tg_id: int, friend_tg_id: int) -> None:
        raise NotImplementedError

    @abstractmethod
    async def remove_incoming_request(
        self, user_tg_id: int, requester_tg_id: int
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, friend_id: uuid.UUID) -> UserFriend | None:
        raise NotImplementedError

    @abstractmethod
    async def update(self, friend: UserFriend) -> UserFriend:
        raise NotImplementedError


class UsersRepository(ABC):
    @abstractmethod
    async def create(self, user: User) -> User:
        raise NotImplementedError

    @abstractmethod
    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        raise NotImplementedError

    @abstractmethod
    async def update(self, user: User) -> User:
        raise NotImplementedError

    @abstractmethod
    async def list_all(self, limit: int = 100, offset: int = 0) -> list[User]:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, telegram_id: int) -> None:
        raise NotImplementedError
