from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.adapters.database.models.user import UserModel
from src.adapters.repositories.exceptions import RepositoryError
from src.domain.entities.user import User
from src.domain.value_objects.coin import Coin
from src.domain.value_objects.experience import Experience
from src.domain.value_objects.telegram_id import TelegramId
from src.ports.repositories.users import UsersRepository


class SQLAlchemyUsersRepository(UsersRepository):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def create(self, user: User) -> User:
        async with self._session_factory() as session:
            model = UserModel(
                telegram_id=user.telegram_id.value,
                username=user.username,
                message_interval=user.time_to_send_message,
                experience=user.experience.points,
                coins=user.coins.amount,
                level=user.level,
                messages_count=user.messages_count,
            )
            session.add(model)
            try:
                await session.commit()
            except IntegrityError as exc:
                await session.rollback()
                raise RepositoryError("Failed to create user") from exc
            await session.refresh(model)
            return self._to_domain(model)

    async def get_by_telegram_id(self, telegram_id: TelegramId) -> User | None:
        async with self._session_factory() as session:
            result = await session.execute(
                select(UserModel).where(UserModel.telegram_id == telegram_id.value)
            )
            model = result.scalar_one_or_none()
            if model is None:
                return None
            return self._to_domain(model)

    async def update(self, user: User) -> User:
        async with self._session_factory() as session:
            stmt = (
                update(UserModel)
                .where(UserModel.telegram_id == user.telegram_id.value)
                .values(
                    username=user.username,
                    message_interval=user.time_to_send_message,
                    experience=user.experience.points,
                    coins=user.coins.amount,
                    level=user.level,
                    messages_count=user.messages_count,
                )
                .returning(UserModel)
            )
            result = await session.execute(stmt)
            model = result.scalar_one_or_none()
            if model is None:
                await session.rollback()
                raise RepositoryError("User does not exist")
            await session.commit()
            return self._to_domain(model)

    @staticmethod
    def _to_domain(model: UserModel) -> User:
        return User(
            telegram_id=TelegramId(model.telegram_id),
            username=model.username or "",
            time_to_send_message=model.message_interval,
            experience=Experience(model.experience),
            coins=Coin(model.coins),
            level=model.level,
            messages_count=model.messages_count,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
