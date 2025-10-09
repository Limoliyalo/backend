from src.domain.entities.picture import Picture
from src.domain.exceptions import PictureNotFoundException
from src.domain.value_objects.telegram_id import TelegramId
from src.ports.repositories.pictures import PicturesRepository


class GetLatestPictureUseCase:
    def __init__(self, pictures_repository: PicturesRepository) -> None:
        self._pictures_repository = pictures_repository

    async def execute(self, telegram_id: int) -> Picture:
        picture = await self._pictures_repository.get_by_owner(TelegramId(telegram_id))
        if picture is None:
            raise PictureNotFoundException(
                message=f"No pictures found for user {telegram_id}"
            )
        return picture
