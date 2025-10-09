from src.domain.entities.user_pictures import UserPictures
from src.domain.exceptions import UserNotFoundException
from src.domain.value_objects.telegram_id import TelegramId
from src.ports.repositories.user_pictures import UserPicturesRepository
from src.ports.repositories.users import UsersRepository


class ListOpenedPicturesUseCase:
    def __init__(
        self,
        users_repository: UsersRepository,
        user_pictures_repository: UserPicturesRepository,
    ) -> None:
        self._users_repository = users_repository
        self._user_pictures_repository = user_pictures_repository

    async def execute(self, telegram_id: int) -> UserPictures:
        user = await self._users_repository.get_by_telegram_id(TelegramId(telegram_id))
        if user is None:
            raise UserNotFoundException(telegram_id)
        return await self._user_pictures_repository.get(TelegramId(telegram_id))
