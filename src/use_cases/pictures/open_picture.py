from dataclasses import dataclass

from src.domain.entities.user_pictures import UserPictures
from src.domain.exceptions import PictureNotFoundException, UserNotFoundException
from src.domain.value_objects.telegram_id import TelegramId
from src.ports.repositories.pictures import PicturesRepository
from src.ports.repositories.user_pictures import UserPicturesRepository
from src.ports.repositories.users import UsersRepository


@dataclass
class OpenPictureInput:
    telegram_id: int
    picture_id: int


class OpenPictureUseCase:
    def __init__(
        self,
        users_repository: UsersRepository,
        pictures_repository: PicturesRepository,
        user_pictures_repository: UserPicturesRepository,
    ) -> None:
        self._users_repository = users_repository
        self._pictures_repository = pictures_repository
        self._user_pictures_repository = user_pictures_repository

    async def execute(self, data: OpenPictureInput) -> UserPictures:
        telegram_id = TelegramId(data.telegram_id)
        user = await self._users_repository.get_by_telegram_id(telegram_id)
        if user is None:
            raise UserNotFoundException(data.telegram_id)

        picture = await self._pictures_repository.get_by_id(
            data.picture_id, telegram_id
        )
        if picture is None:
            raise PictureNotFoundException(data.picture_id)

        if not picture.is_opened:
            picture.open(user)
            await self._users_repository.update(user)
            await self._pictures_repository.update(picture)

        return await self._user_pictures_repository.get(telegram_id)
