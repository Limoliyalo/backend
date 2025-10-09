from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.adapters.database.models.picture import PictureModel
from src.adapters.repositories.exceptions import RepositoryError
from src.domain.entities.user_pictures import UserPictures
from src.domain.value_objects.telegram_id import TelegramId
from src.ports.repositories.user_pictures import UserPicturesRepository


class SQLAlchemyUserPicturesRepository(UserPicturesRepository):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def get(self, telegram_id: TelegramId) -> UserPictures:
        async with self._session_factory() as session:
            result = await session.execute(
                select(PictureModel.picture_id).where(
                    PictureModel.telegram_id == telegram_id.value,
                    PictureModel.is_opened.is_(True),
                )
            )
            opened = list(result.scalars().all())
        return UserPictures(telegram_id=telegram_id, opened_pictures=opened)

    async def add_picture(
        self, telegram_id: TelegramId, picture_id: int
    ) -> UserPictures:
        async with self._session_factory() as session:
            stmt = (
                update(PictureModel)
                .where(
                    PictureModel.telegram_id == telegram_id.value,
                    PictureModel.picture_id == picture_id,
                )
                .values(is_opened=True, opened_at=datetime.now(timezone.utc))
            )
            result = await session.execute(stmt)
            if result.rowcount == 0:
                await session.rollback()
                raise RepositoryError("Picture not found")
            await session.commit()

        return await self.get(telegram_id)
