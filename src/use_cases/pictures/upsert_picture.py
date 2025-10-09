from dataclasses import dataclass

from src.domain.entities.picture import Picture
from src.domain.value_objects.telegram_id import TelegramId
from src.ports.repositories.pictures import PicturesRepository


@dataclass
class UpsertPictureInput:
    picture_id: int
    telegram_id: int
    level_to_open: int
    price: int


class UpsertPictureUseCase:
    def __init__(self, pictures_repository: PicturesRepository) -> None:
        self._pictures_repository = pictures_repository

    async def execute(self, data: UpsertPictureInput) -> Picture:
        telegram_id = TelegramId(data.telegram_id)
        existing = await self._pictures_repository.get_by_id(
            data.picture_id, telegram_id
        )

        picture = Picture(
            id=data.picture_id,
            telegram_id=telegram_id,
            level_to_open=data.level_to_open,
            price=data.price,
            is_opened=existing.is_opened if existing else False,
            opened_at=existing.opened_at if existing else None,
        )

        if existing:
            return await self._pictures_repository.update(picture)

        return await self._pictures_repository.create(picture)
