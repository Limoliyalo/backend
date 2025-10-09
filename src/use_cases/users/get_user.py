from src.domain.exceptions import UserNotFoundException
from src.domain.entities.user import User
from src.domain.value_objects.telegram_id import TelegramId
from src.ports.repositories.users import UsersRepository


class GetUserUseCase:
    def __init__(self, users_repository: UsersRepository) -> None:
        self._users_repository = users_repository

    async def execute(self, telegram_id: int) -> User:
        user = await self._users_repository.get_by_telegram_id(TelegramId(telegram_id))
        if user is None:
            raise UserNotFoundException(telegram_id)
        return user
