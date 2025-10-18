import uuid
from dataclasses import dataclass
from datetime import time

from src.domain.entities.healthity.users import UserSettings
from src.domain.exceptions import EntityNotFoundException
from src.domain.value_objects.telegram_id import TelegramId
from src.ports.repositories.healthity.users import UserSettingsRepository


@dataclass
class CreateUserSettingsInput:
    user_tg_id: int
    quiet_start_time: time | None = None
    quiet_end_time: time | None = None
    muted_days: list[str] | None = None
    do_not_disturb: bool = False


@dataclass
class UpdateUserSettingsInput:
    user_tg_id: int
    quiet_start_time: time | None = None
    quiet_end_time: time | None = None
    muted_days: list[str] | None = None
    do_not_disturb: bool | None = None


class ListUserSettingsUseCase:
    def __init__(self, settings_repository: UserSettingsRepository) -> None:
        self._settings_repository = settings_repository

    async def execute(self) -> list[UserSettings]:
        return await self._settings_repository.list_all()


class GetUserSettingsUseCase:
    def __init__(self, settings_repository: UserSettingsRepository) -> None:
        self._settings_repository = settings_repository

    async def execute(self, user_tg_id: int) -> UserSettings:
        settings = await self._settings_repository.get_by_user(TelegramId(user_tg_id))
        if settings is None:
            raise EntityNotFoundException(f"Settings for user {user_tg_id} not found")
        return settings


class UpsertUserSettingsUseCase:
    def __init__(self, settings_repository: UserSettingsRepository) -> None:
        self._settings_repository = settings_repository

    async def execute(self, data: UpdateUserSettingsInput) -> UserSettings:
        settings = await self._settings_repository.get_by_user(
            TelegramId(data.user_tg_id)
        )

        if settings is None:

            settings = UserSettings(
                id=uuid.uuid4(),
                user_tg_id=TelegramId(data.user_tg_id),
                quiet_start_time=data.quiet_start_time,
                quiet_end_time=data.quiet_end_time,
                muted_days=data.muted_days or [],
                do_not_disturb=data.do_not_disturb or False,
            )
        else:

            if data.quiet_start_time is not None:
                settings.quiet_start_time = data.quiet_start_time
            if data.quiet_end_time is not None:
                settings.quiet_end_time = data.quiet_end_time
            if data.muted_days is not None:
                settings.set_muted_days(data.muted_days)
            if data.do_not_disturb is not None:
                settings.toggle_do_not_disturb(data.do_not_disturb)

        return await self._settings_repository.upsert(settings)


class DeleteUserSettingsUseCase:
    def __init__(self, settings_repository: UserSettingsRepository) -> None:
        self._settings_repository = settings_repository

    async def execute(self, user_tg_id: int) -> None:
        settings = await self._settings_repository.get_by_user(TelegramId(user_tg_id))
        if settings is None:
            raise EntityNotFoundException(f"Settings for user {user_tg_id} not found")
        await self._settings_repository.delete(settings.id)
