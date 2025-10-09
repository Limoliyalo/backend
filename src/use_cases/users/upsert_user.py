from dataclasses import dataclass
from datetime import datetime, timezone

from src.domain.entities.user import User
from src.domain.value_objects.coin import Coin
from src.domain.value_objects.experience import Experience
from src.domain.value_objects.telegram_id import TelegramId
from src.ports.repositories.users import UsersRepository


@dataclass
class UpsertUserInput:
    telegram_id: int
    timer: int
    experience: int
    coins: int
    username: str
    level_cnt: int = 0
    message_count: int = 0


class UpsertUserUseCase:
    def __init__(self, users_repository: UsersRepository) -> None:
        self._users_repository = users_repository

    async def execute(self, data: UpsertUserInput) -> User:
        telegram_id = TelegramId(data.telegram_id)
        existing = await self._users_repository.get_by_telegram_id(telegram_id)

        user = User(
            telegram_id=telegram_id,
            username=data.username,
            time_to_send_message=data.timer,
            experience=Experience(data.experience),
            coins=Coin(data.coins),
            level=data.level_cnt,
            messages_count=data.message_count,
        )

        if existing:
            user.created_at = existing.created_at
            user.updated_at = datetime.now(timezone.utc)
            return await self._users_repository.update(user)

        return await self._users_repository.create(user)
