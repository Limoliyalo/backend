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


@dataclass
class PatchUserSettingsInput:
    user_tg_id: int
    quiet_start_time: time | None = None
    quiet_end_time: time | None = None
    muted_days: list[str] | None = None
    do_not_disturb: bool | None = None
    # Флаги для отслеживания переданных полей
    _quiet_start_time_provided: bool = False
    _quiet_end_time_provided: bool = False
    _muted_days_provided: bool = False
    _do_not_disturb_provided: bool = False


@dataclass
class UpdateMutedDaysInput:
    user_tg_id: int
    muted_days: list[str]


@dataclass
class UpdateDoNotDisturbInput:
    user_tg_id: int
    do_not_disturb: bool


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


class PatchUserSettingsUseCase:
    def __init__(self, settings_repository: UserSettingsRepository) -> None:
        self._settings_repository = settings_repository

    async def execute(self, data: PatchUserSettingsInput) -> UserSettings:
        settings = await self._settings_repository.get_by_user(
            TelegramId(data.user_tg_id)
        )

        if settings is None:
            # Создаем новые настройки
            settings = UserSettings(
                id=uuid.uuid4(),
                user_tg_id=TelegramId(data.user_tg_id),
                quiet_start_time=(
                    data.quiet_start_time if data._quiet_start_time_provided else None
                ),
                quiet_end_time=(
                    data.quiet_end_time if data._quiet_end_time_provided else None
                ),
                muted_days=data.muted_days if data._muted_days_provided else [],
                do_not_disturb=(
                    data.do_not_disturb if data._do_not_disturb_provided else False
                ),
            )
        else:
            # Обновляем только переданные поля
            if data._quiet_start_time_provided:
                settings.quiet_start_time = data.quiet_start_time
            if data._quiet_end_time_provided:
                settings.quiet_end_time = data.quiet_end_time
            if data._muted_days_provided:
                settings.set_muted_days(data.muted_days or [])
            if data._do_not_disturb_provided:
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


class ResetQuietStartTimeUseCase:
    def __init__(self, settings_repository: UserSettingsRepository) -> None:
        self._settings_repository = settings_repository

    async def execute(self, user_tg_id: int) -> UserSettings:
        settings = await self._settings_repository.get_by_user(TelegramId(user_tg_id))

        if settings is None:
            # Создаем новые настройки с null для quiet_start_time
            settings = UserSettings(
                id=uuid.uuid4(),
                user_tg_id=TelegramId(user_tg_id),
                quiet_start_time=None,
                quiet_end_time=None,
                muted_days=[],
                do_not_disturb=False,
            )
        else:
            # Сбрасываем только quiet_start_time
            settings.quiet_start_time = None

        return await self._settings_repository.upsert(settings)


class ResetQuietEndTimeUseCase:
    def __init__(self, settings_repository: UserSettingsRepository) -> None:
        self._settings_repository = settings_repository

    async def execute(self, user_tg_id: int) -> UserSettings:
        settings = await self._settings_repository.get_by_user(TelegramId(user_tg_id))

        if settings is None:
            # Создаем новые настройки с null для quiet_end_time
            settings = UserSettings(
                id=uuid.uuid4(),
                user_tg_id=TelegramId(user_tg_id),
                quiet_start_time=None,
                quiet_end_time=None,
                muted_days=[],
                do_not_disturb=False,
            )
        else:
            # Сбрасываем только quiet_end_time
            settings.quiet_end_time = None

        return await self._settings_repository.upsert(settings)


class UpdateMutedDaysUseCase:
    def __init__(self, settings_repository: UserSettingsRepository) -> None:
        self._settings_repository = settings_repository

    async def execute(self, data: UpdateMutedDaysInput) -> UserSettings:
        settings = await self._settings_repository.get_by_user(
            TelegramId(data.user_tg_id)
        )

        if settings is None:
            # Создаем новые настройки
            settings = UserSettings(
                id=uuid.uuid4(),
                user_tg_id=TelegramId(data.user_tg_id),
                quiet_start_time=None,
                quiet_end_time=None,
                muted_days=data.muted_days,
                do_not_disturb=False,
            )
        else:
            # Обновляем только muted_days
            settings.set_muted_days(data.muted_days)

        return await self._settings_repository.upsert(settings)


class UpdateDoNotDisturbUseCase:
    def __init__(self, settings_repository: UserSettingsRepository) -> None:
        self._settings_repository = settings_repository

    async def execute(self, data: UpdateDoNotDisturbInput) -> UserSettings:
        settings = await self._settings_repository.get_by_user(
            TelegramId(data.user_tg_id)
        )

        if settings is None:
            # Создаем новые настройки
            settings = UserSettings(
                id=uuid.uuid4(),
                user_tg_id=TelegramId(data.user_tg_id),
                quiet_start_time=None,
                quiet_end_time=None,
                muted_days=[],
                do_not_disturb=data.do_not_disturb,
            )
        else:
            # Обновляем только do_not_disturb
            settings.toggle_do_not_disturb(data.do_not_disturb)

        return await self._settings_repository.upsert(settings)
