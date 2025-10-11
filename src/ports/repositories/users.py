from abc import ABC, abstractmethod
from src.domain.entities.healthity.users import User
from src.domain.value_objects.telegram_id import TelegramId


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
