import logging
from collections.abc import Callable

from sqlalchemy import delete, select

from src.adapters.database.models.user import UserModel
from src.adapters.database.models.user_friends import UserFriendModel
from src.adapters.database.models.user_settings import UserSettingsModel
from src.adapters.database.uow import AbstractUnitOfWork
from src.adapters.repositories.base import SQLAlchemyRepository
from src.adapters.repositories.exceptions import RepositoryError
from src.domain.entities.healthity.users import User, UserFriend, UserSettings
from src.domain.value_objects.telegram_id import TelegramId
from src.ports.repositories.healthity.users import (
    UserFriendsRepository,
    UserSettingsRepository,
)
from src.ports.repositories.users import UsersRepository


class SQLAlchemyUserSettingsRepository(
    SQLAlchemyRepository[UserSettingsModel], UserSettingsRepository
):
    model = UserSettingsModel

    def __init__(self, uow_factory: Callable[[], AbstractUnitOfWork]) -> None:
        super().__init__(uow_factory)

    async def get_by_user(self, user_tg_id: TelegramId) -> UserSettings | None:
        model = await self.first(filters={"user_tg_id": user_tg_id.value})
        if model is None:
            return None
        return self._to_domain(model)

    async def upsert(self, settings: UserSettings) -> UserSettings:
        async with self._uow() as uow:
            model = await uow.session.get(UserSettingsModel, settings.id)
            if model is None:
                model = UserSettingsModel(
                    id=settings.id,
                    user_tg_id=settings.user_tg_id.value,
                    quiet_start_time=settings.quiet_start_time,
                    quiet_end_time=settings.quiet_end_time,
                    muted_days=settings.muted_days,
                    do_not_disturb=settings.do_not_disturb,
                )
                uow.session.add(model)
            else:
                model.quiet_start_time = settings.quiet_start_time
                model.quiet_end_time = settings.quiet_end_time
                model.muted_days = list(settings.muted_days)
                model.do_not_disturb = settings.do_not_disturb

            await uow.session.flush()
            await uow.session.refresh(model)
            return self._to_domain(model)

    @staticmethod
    def _to_domain(model: UserSettingsModel) -> UserSettings:
        return UserSettings(
            id=model.id,
            user_tg_id=TelegramId(model.user_tg_id),
            quiet_start_time=model.quiet_start_time,
            quiet_end_time=model.quiet_end_time,
            muted_days=list(model.muted_days or []),
            do_not_disturb=model.do_not_disturb,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )


class SQLAlchemyUserFriendsRepository(
    SQLAlchemyRepository[UserFriendModel], UserFriendsRepository
):
    model = UserFriendModel

    def __init__(self, uow_factory: Callable[[], AbstractUnitOfWork]) -> None:
        super().__init__(uow_factory)

    async def list_for_user(self, owner_tg_id: TelegramId) -> list[UserFriend]:
        async with self._uow() as uow:
            result = await uow.session.execute(
                select(UserFriendModel).where(
                    UserFriendModel.owner_tg_id == owner_tg_id.value
                )
            )
            models = result.scalars().all()
        return [self._to_domain(model) for model in models]

    async def add(self, friend: UserFriend) -> UserFriend:
        model = UserFriendModel(
            id=friend.id,
            owner_tg_id=friend.owner_tg_id.value,
            friend_tg_id=friend.friend_tg_id.value,
        )
        saved_model = await super().add(model)
        return self._to_domain(saved_model)

    async def remove(self, owner_tg_id: TelegramId, friend_tg_id: TelegramId) -> None:
        async with self._uow() as uow:
            result = await uow.session.execute(
                delete(UserFriendModel).where(
                    UserFriendModel.owner_tg_id == owner_tg_id.value,
                    UserFriendModel.friend_tg_id == friend_tg_id.value,
                )
            )
            if result.rowcount == 0:
                raise RepositoryError("Friend linkage not found")

    @staticmethod
    def _to_domain(model: UserFriendModel) -> UserFriend:
        return UserFriend(
            id=model.id,
            owner_tg_id=TelegramId(model.owner_tg_id),
            friend_tg_id=TelegramId(model.friend_tg_id),
            created_at=model.created_at,
        )


class SQLAlchemyUsersRepository(SQLAlchemyRepository[UserModel], UsersRepository):
    model = UserModel

    def __init__(self, uow_factory: Callable[[], AbstractUnitOfWork]) -> None:
        super().__init__(uow_factory)
        self.logger = logging.getLogger(self.__class__.__name__)

    async def create(self, user: User) -> User:
        self.logger.debug({
            "action": "SQLAlchemyUsersRepository.create",
            "stage": "start",
            "data": {
                "telegram_id": user.telegram_id.value,
                "is_active": user.is_active,
                "balance": user.balance
            }
        })
        
        model = UserModel(
            tg_id=user.telegram_id.value,
            password_hash=user.password_hash,
            is_active=user.is_active,
            balance=user.balance,
        )
        saved = await self.add(model)
        
        self.logger.info({
            "action": "SQLAlchemyUsersRepository.create",
            "stage": "end",
            "data": {"telegram_id": user.telegram_id.value}
        })
        return self._to_domain(saved)

    async def get_by_telegram_id(self, telegram_id: TelegramId) -> User | None:
        self.logger.debug({
            "action": "SQLAlchemyUsersRepository.get_by_telegram_id",
            "stage": "start",
            "data": {"telegram_id": telegram_id.value}
        })
        
        model = await self.first(filters={"tg_id": telegram_id.value})
        
        if model is None:
            self.logger.debug({
                "action": "SQLAlchemyUsersRepository.get_by_telegram_id",
                "stage": "not_found",
                "data": {"telegram_id": telegram_id.value}
            })
            return None
        
        self.logger.debug({
            "action": "SQLAlchemyUsersRepository.get_by_telegram_id",
            "stage": "end",
            "data": {"telegram_id": telegram_id.value, "found": True}
        })
        return self._to_domain(model)

    async def update(self, user: User) -> User:
        self.logger.debug({
            "action": "SQLAlchemyUsersRepository.update",
            "stage": "start",
            "data": {
                "telegram_id": user.telegram_id.value,
                "is_active": user.is_active,
                "balance": user.balance
            }
        })
        
        async with self._uow() as uow:
            result = await uow.session.execute(
                select(UserModel).where(UserModel.tg_id == user.telegram_id.value)
            )
            model = result.scalar_one_or_none()
            if model is None:
                self.logger.error({
                    "action": "SQLAlchemyUsersRepository.update",
                    "stage": "not_found",
                    "data": {"telegram_id": user.telegram_id.value}
                })
                raise RepositoryError("User does not exist")

            model.password_hash = user.password_hash
            model.is_active = user.is_active
            model.balance = user.balance

            await uow.session.flush()
            await uow.session.refresh(model)
            
            self.logger.info({
                "action": "SQLAlchemyUsersRepository.update",
                "stage": "end",
                "data": {"telegram_id": user.telegram_id.value}
            })
            return self._to_domain(model)

    async def list_all(self, limit: int = 100, offset: int = 0) -> list[User]:
        async with self._uow() as uow:
            result = await uow.session.execute(
                select(UserModel).limit(limit).offset(offset)
            )
            models = result.scalars().all()
        return [self._to_domain(model) for model in models]

    async def delete(self, telegram_id: TelegramId) -> None:
        async with self._uow() as uow:
            result = await uow.session.execute(
                delete(UserModel).where(UserModel.tg_id == telegram_id.value)
            )
            if result.rowcount == 0:
                raise RepositoryError("User not found")

    @staticmethod
    def _to_domain(model: UserModel) -> User:
        return User(
            telegram_id=TelegramId(model.tg_id),
            password_hash=model.password_hash,
            is_active=model.is_active,
            balance=model.balance,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
