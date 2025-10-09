from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.adapters.database.models.picture import PictureModel
from src.adapters.repositories.exceptions import RepositoryError
from src.domain.entities.picture import Picture
from src.domain.value_objects.telegram_id import TelegramId
from src.ports.repositories.pictures import PicturesRepository


class SQLAlchemyPicturesRepository(PicturesRepository):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def create(self, picture: Picture) -> Picture:
        async with self._session_factory() as session:
            model = PictureModel(
                picture_id=picture.id,
                telegram_id=picture.telegram_id.value,
                level_to_open=picture.level_to_open,
                price=picture.price,
                is_opened=picture.is_opened,
                opened_at=picture.opened_at,
            )
            session.add(model)
            try:
                await session.commit()
            except IntegrityError as exc:
                await session.rollback()
                raise RepositoryError("Failed to create picture") from exc
            await session.refresh(model)
            return self._to_domain(model)

    async def get_by_owner(self, telegram_id: TelegramId) -> Picture | None:
        async with self._session_factory() as session:
            result = await session.execute(
                select(PictureModel)
                .where(PictureModel.telegram_id == telegram_id.value)
                .order_by(PictureModel.id.desc())
            )
            model = result.scalars().first()
            if model is None:
                return None
            return self._to_domain(model)

    async def get_by_id(
        self, picture_id: int, telegram_id: TelegramId
    ) -> Picture | None:
        async with self._session_factory() as session:
            result = await session.execute(
                select(PictureModel).where(
                    PictureModel.picture_id == picture_id,
                    PictureModel.telegram_id == telegram_id.value,
                )
            )
            model = result.scalar_one_or_none()
            if model is None:
                return None
            return self._to_domain(model)

    async def mark_opened(self, picture_id: int, telegram_id: TelegramId) -> None:
        async with self._session_factory() as session:
            stmt = (
                update(PictureModel)
                .where(
                    PictureModel.picture_id == picture_id,
                    PictureModel.telegram_id == telegram_id.value,
                )
                .values(is_opened=True, opened_at=datetime.now(timezone.utc))
            )
            result = await session.execute(stmt)
            if result.rowcount == 0:
                await session.rollback()
                raise RepositoryError("Picture not found")
            await session.commit()

    async def update(self, picture: Picture) -> Picture:
        async with self._session_factory() as session:
            stmt = (
                update(PictureModel)
                .where(
                    PictureModel.picture_id == picture.id,
                    PictureModel.telegram_id == picture.telegram_id.value,
                )
                .values(
                    level_to_open=picture.level_to_open,
                    price=picture.price,
                    is_opened=picture.is_opened,
                    opened_at=picture.opened_at,
                )
                .returning(PictureModel)
            )
            result = await session.execute(stmt)
            model = result.scalar_one_or_none()
            if model is None:
                await session.rollback()
                raise RepositoryError("Picture not found")
            await session.commit()
            return self._to_domain(model)

    @staticmethod
    def _to_domain(model: PictureModel) -> Picture:
        return Picture(
            id=model.picture_id,
            telegram_id=TelegramId(model.telegram_id),
            level_to_open=model.level_to_open,
            price=model.price,
            is_opened=model.is_opened,
            opened_at=model.opened_at,
        )
