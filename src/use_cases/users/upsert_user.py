from dataclasses import dataclass

from src.domain.entities.healthity.users import User
from src.domain.value_objects.telegram_id import TelegramId
from src.ports.repositories.users import UsersRepository


@dataclass
class UpsertUserInput:
    telegram_id: int
    password_hash: str | None = None
    is_active: bool = True
    balance: int = 0


class UpsertUserUseCase:
    def __init__(self, users_repository: UsersRepository) -> None:
        self._users_repository = users_repository

    async def execute(self, data: UpsertUserInput) -> User:
        telegram_id = TelegramId(data.telegram_id)
        existing = await self._users_repository.get_by_telegram_id(telegram_id)

        user = User(
            telegram_id=telegram_id,
            password_hash=data.password_hash,
            is_active=data.is_active,
            balance=data.balance,
        )

        if existing:
            user.created_at = existing.created_at
            user.updated_at = existing.updated_at
            return await self._users_repository.update(user)

        return await self._users_repository.create(user)
