from dependency_injector import containers, providers

from src.adapters.database.session import session_manager
from src.adapters.database.uow import SQLAlchemyUnitOfWork
from src.adapters.repositories.healthity import (
    SQLAlchemyActivityTypesRepository,
    SQLAlchemyBackgroundsRepository,
    SQLAlchemyCharacterBackgroundsRepository,
    SQLAlchemyCharacterItemsRepository,
    SQLAlchemyCharactersRepository,
    SQLAlchemyDailyActivitiesRepository,
    SQLAlchemyDailyProgressRepository,
    SQLAlchemyItemBackgroundPositionsRepository,
    SQLAlchemyItemCategoriesRepository,
    SQLAlchemyItemsRepository,
    SQLAlchemyMoodHistoryRepository,
    SQLAlchemyTransactionsRepository,
    SQLAlchemyUserFriendsRepository,
    SQLAlchemyUserSettingsRepository,
    SQLAlchemyUsersRepository,
)
from src.core.settings import settings
from src.use_cases.users.get_user import GetUserUseCase
from src.use_cases.users.upsert_user import UpsertUserUseCase


class ApplicationContainer(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(packages=["src.drivers.rest"])

    settings_provider = providers.Object(settings)

    session_factory = providers.Object(session_manager.async_session)
    unit_of_work = providers.Factory(
        SQLAlchemyUnitOfWork, session_factory=session_factory
    )

    users_repository = providers.Factory(
        SQLAlchemyUsersRepository, uow_factory=unit_of_work.provider
    )
    user_settings_repository = providers.Factory(
        SQLAlchemyUserSettingsRepository, uow_factory=unit_of_work.provider
    )
    user_friends_repository = providers.Factory(
        SQLAlchemyUserFriendsRepository, uow_factory=unit_of_work.provider
    )
    item_categories_repository = providers.Factory(
        SQLAlchemyItemCategoriesRepository, uow_factory=unit_of_work.provider
    )
    items_repository = providers.Factory(
        SQLAlchemyItemsRepository, uow_factory=unit_of_work.provider
    )
    backgrounds_repository = providers.Factory(
        SQLAlchemyBackgroundsRepository, uow_factory=unit_of_work.provider
    )
    characters_repository = providers.Factory(
        SQLAlchemyCharactersRepository, uow_factory=unit_of_work.provider
    )
    character_items_repository = providers.Factory(
        SQLAlchemyCharacterItemsRepository, uow_factory=unit_of_work.provider
    )
    character_backgrounds_repository = providers.Factory(
        SQLAlchemyCharacterBackgroundsRepository, uow_factory=unit_of_work.provider
    )
    item_background_positions_repository = providers.Factory(
        SQLAlchemyItemBackgroundPositionsRepository, uow_factory=unit_of_work.provider
    )
    activity_types_repository = providers.Factory(
        SQLAlchemyActivityTypesRepository, uow_factory=unit_of_work.provider
    )
    daily_activities_repository = providers.Factory(
        SQLAlchemyDailyActivitiesRepository, uow_factory=unit_of_work.provider
    )
    daily_progress_repository = providers.Factory(
        SQLAlchemyDailyProgressRepository, uow_factory=unit_of_work.provider
    )
    mood_history_repository = providers.Factory(
        SQLAlchemyMoodHistoryRepository, uow_factory=unit_of_work.provider
    )
    transactions_repository = providers.Factory(
        SQLAlchemyTransactionsRepository, uow_factory=unit_of_work.provider
    )

    get_user_use_case = providers.Factory(
        GetUserUseCase, users_repository=users_repository
    )
    upsert_user_use_case = providers.Factory(
        UpsertUserUseCase, users_repository=users_repository
    )
