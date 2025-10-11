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
from src.core.security import PasswordHasher
from src.use_cases.users.manage_users import (
    GetUserUseCase,
    CreateUserUseCase,
    ListUsersUseCase,
    UpdateUserUseCase,
    DeleteUserUseCase,
)
from src.use_cases.characters.create_character import CreateCharacterUseCase
from src.use_cases.characters.get_character import (
    GetCharacterByIdUseCase,
    GetCharacterByUserUseCase,
    ListCharactersUseCase,
)
from src.use_cases.characters.update_character import UpdateCharacterUseCase
from src.use_cases.characters.delete_character import DeleteCharacterUseCase
from src.use_cases.items.manage_items import (
    CreateItemUseCase,
    GetItemUseCase,
    ListItemsUseCase,
    ListAvailableItemsUseCase,
    UpdateItemUseCase,
    DeleteItemUseCase,
)
from src.use_cases.backgrounds.manage_backgrounds import (
    CreateBackgroundUseCase,
    GetBackgroundUseCase,
    ListBackgroundsUseCase,
    ListAvailableBackgroundsUseCase,
    UpdateBackgroundUseCase,
    DeleteBackgroundUseCase,
)
from src.use_cases.transactions.manage_transactions import (
    CreateTransactionUseCase,
    DeleteTransactionUseCase,
    GetTransactionUseCase,
    ListTransactionsForUserUseCase,
    UpdateTransactionUseCase,
)
from src.use_cases.user_settings.manage_settings import (
    DeleteUserSettingsUseCase,
    GetUserSettingsUseCase,
    ListUserSettingsUseCase,
    UpsertUserSettingsUseCase,
)
from src.use_cases.activity_types.manage_activity_types import (
    CreateActivityTypeUseCase,
    DeleteActivityTypeUseCase,
    GetActivityTypeByNameUseCase,
    GetActivityTypeUseCase,
    ListActivityTypesUseCase,
    UpdateActivityTypeUseCase,
)
from src.use_cases.daily_activities.manage_daily_activities import (
    CreateDailyActivityUseCase,
    DeleteDailyActivityUseCase,
    GetDailyActivityUseCase,
    ListDailyActivitiesForDayUseCase,
    UpdateDailyActivityUseCase,
)
from src.use_cases.daily_progress.manage_daily_progress import (
    CreateDailyProgressUseCase,
    DeleteDailyProgressUseCase,
    GetDailyProgressForDayUseCase,
    GetDailyProgressUseCase,
    ListDailyProgressForCharacterUseCase,
    UpdateDailyProgressUseCase,
)
from src.use_cases.mood_history.manage_mood_history import (
    CreateMoodHistoryUseCase,
    DeleteMoodHistoryUseCase,
    GetMoodHistoryUseCase,
    ListMoodHistoryForCharacterUseCase,
    UpdateMoodHistoryUseCase,
)
from src.use_cases.user_friends.manage_user_friends import (
    AddFriendUseCase,
    GetUserFriendUseCase,
    ListUserFriendsUseCase,
    RemoveFriendUseCase,
    UpdateUserFriendUseCase,
)
from src.use_cases.character_items.manage_character_items import (
    GetCharacterItemUseCase,
    ListCharacterItemsUseCase,
    PurchaseItemUseCase,
    RemoveCharacterItemUseCase,
    UpdateCharacterItemUseCase,
)
from src.use_cases.character_backgrounds.manage_character_backgrounds import (
    GetCharacterBackgroundUseCase,
    ListCharacterBackgroundsUseCase,
    PurchaseBackgroundUseCase,
    RemoveCharacterBackgroundUseCase,
    UpdateCharacterBackgroundUseCase,
)
from src.use_cases.item_categories.manage_item_categories import (
    ListItemCategoriesUseCase,
    GetItemCategoryUseCase,
    CreateItemCategoryUseCase,
    UpdateItemCategoryUseCase,
    DeleteItemCategoryUseCase,
)
from src.use_cases.item_background_positions.manage_positions import (
    ListPositionsForItemUseCase,
    GetPositionUseCase,
    CreatePositionUseCase,
    UpdatePositionUseCase,
    DeletePositionUseCase,
)


class ApplicationContainer(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(packages=["src.drivers.rest"])

    settings_provider = providers.Object(settings)
    password_hasher = providers.Singleton(PasswordHasher)

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

    # User use cases
    get_user_use_case = providers.Factory(
        GetUserUseCase, users_repository=users_repository
    )
    create_user_use_case = providers.Factory(
        CreateUserUseCase,
        users_repository=users_repository,
        password_hasher=password_hasher,
    )
    list_users_use_case = providers.Factory(
        ListUsersUseCase, users_repository=users_repository
    )
    update_user_use_case = providers.Factory(
        UpdateUserUseCase,
        users_repository=users_repository,
        password_hasher=password_hasher,
    )
    delete_user_use_case = providers.Factory(
        DeleteUserUseCase, users_repository=users_repository
    )

    # Character use cases
    create_character_use_case = providers.Factory(
        CreateCharacterUseCase, characters_repository=characters_repository
    )
    get_character_by_id_use_case = providers.Factory(
        GetCharacterByIdUseCase, characters_repository=characters_repository
    )
    get_character_by_user_use_case = providers.Factory(
        GetCharacterByUserUseCase, characters_repository=characters_repository
    )
    list_characters_use_case = providers.Factory(
        ListCharactersUseCase, characters_repository=characters_repository
    )
    update_character_use_case = providers.Factory(
        UpdateCharacterUseCase, characters_repository=characters_repository
    )
    delete_character_use_case = providers.Factory(
        DeleteCharacterUseCase, characters_repository=characters_repository
    )

    # Item use cases
    create_item_use_case = providers.Factory(
        CreateItemUseCase, items_repository=items_repository
    )
    get_item_use_case = providers.Factory(
        GetItemUseCase, items_repository=items_repository
    )
    list_items_use_case = providers.Factory(
        ListItemsUseCase, items_repository=items_repository
    )
    list_available_items_use_case = providers.Factory(
        ListAvailableItemsUseCase, items_repository=items_repository
    )
    update_item_use_case = providers.Factory(
        UpdateItemUseCase, items_repository=items_repository
    )
    delete_item_use_case = providers.Factory(
        DeleteItemUseCase, items_repository=items_repository
    )

    # Background use cases
    create_background_use_case = providers.Factory(
        CreateBackgroundUseCase, backgrounds_repository=backgrounds_repository
    )
    get_background_use_case = providers.Factory(
        GetBackgroundUseCase, backgrounds_repository=backgrounds_repository
    )
    list_backgrounds_use_case = providers.Factory(
        ListBackgroundsUseCase, backgrounds_repository=backgrounds_repository
    )
    list_available_backgrounds_use_case = providers.Factory(
        ListAvailableBackgroundsUseCase, backgrounds_repository=backgrounds_repository
    )
    update_background_use_case = providers.Factory(
        UpdateBackgroundUseCase, backgrounds_repository=backgrounds_repository
    )
    delete_background_use_case = providers.Factory(
        DeleteBackgroundUseCase, backgrounds_repository=backgrounds_repository
    )

    # Transaction use cases
    create_transaction_use_case = providers.Factory(
        CreateTransactionUseCase, transactions_repository=transactions_repository
    )
    get_transaction_use_case = providers.Factory(
        GetTransactionUseCase, transactions_repository=transactions_repository
    )
    list_transactions_for_user_use_case = providers.Factory(
        ListTransactionsForUserUseCase, transactions_repository=transactions_repository
    )
    update_transaction_use_case = providers.Factory(
        UpdateTransactionUseCase, transactions_repository=transactions_repository
    )
    delete_transaction_use_case = providers.Factory(
        DeleteTransactionUseCase, transactions_repository=transactions_repository
    )

    # User settings use cases
    list_user_settings_use_case = providers.Factory(
        ListUserSettingsUseCase, settings_repository=user_settings_repository
    )
    get_user_settings_use_case = providers.Factory(
        GetUserSettingsUseCase, settings_repository=user_settings_repository
    )
    upsert_user_settings_use_case = providers.Factory(
        UpsertUserSettingsUseCase, settings_repository=user_settings_repository
    )
    delete_user_settings_use_case = providers.Factory(
        DeleteUserSettingsUseCase, settings_repository=user_settings_repository
    )

    # Activity Types use cases
    create_activity_type_use_case = providers.Factory(
        CreateActivityTypeUseCase, activity_types_repository=activity_types_repository
    )
    get_activity_type_use_case = providers.Factory(
        GetActivityTypeUseCase, activity_types_repository=activity_types_repository
    )
    get_activity_type_by_name_use_case = providers.Factory(
        GetActivityTypeByNameUseCase,
        activity_types_repository=activity_types_repository,
    )
    list_activity_types_use_case = providers.Factory(
        ListActivityTypesUseCase, activity_types_repository=activity_types_repository
    )
    update_activity_type_use_case = providers.Factory(
        UpdateActivityTypeUseCase, activity_types_repository=activity_types_repository
    )
    delete_activity_type_use_case = providers.Factory(
        DeleteActivityTypeUseCase, activity_types_repository=activity_types_repository
    )

    # Daily Activities use cases
    create_daily_activity_use_case = providers.Factory(
        CreateDailyActivityUseCase,
        daily_activities_repository=daily_activities_repository,
    )
    list_daily_activities_for_day_use_case = providers.Factory(
        ListDailyActivitiesForDayUseCase,
        daily_activities_repository=daily_activities_repository,
    )
    get_daily_activity_use_case = providers.Factory(
        GetDailyActivityUseCase,
        daily_activities_repository=daily_activities_repository,
    )
    update_daily_activity_use_case = providers.Factory(
        UpdateDailyActivityUseCase,
        daily_activities_repository=daily_activities_repository,
    )
    delete_daily_activity_use_case = providers.Factory(
        DeleteDailyActivityUseCase,
        daily_activities_repository=daily_activities_repository,
    )

    # Daily Progress use cases
    create_daily_progress_use_case = providers.Factory(
        CreateDailyProgressUseCase, daily_progress_repository=daily_progress_repository
    )
    list_daily_progress_for_character_use_case = providers.Factory(
        ListDailyProgressForCharacterUseCase,
        daily_progress_repository=daily_progress_repository,
    )
    get_daily_progress_for_day_use_case = providers.Factory(
        GetDailyProgressForDayUseCase,
        daily_progress_repository=daily_progress_repository,
    )
    get_daily_progress_use_case = providers.Factory(
        GetDailyProgressUseCase,
        daily_progress_repository=daily_progress_repository,
    )
    update_daily_progress_use_case = providers.Factory(
        UpdateDailyProgressUseCase,
        daily_progress_repository=daily_progress_repository,
    )
    delete_daily_progress_use_case = providers.Factory(
        DeleteDailyProgressUseCase,
        daily_progress_repository=daily_progress_repository,
    )

    # Mood History use cases
    create_mood_history_use_case = providers.Factory(
        CreateMoodHistoryUseCase, mood_history_repository=mood_history_repository
    )
    list_mood_history_for_character_use_case = providers.Factory(
        ListMoodHistoryForCharacterUseCase,
        mood_history_repository=mood_history_repository,
    )
    get_mood_history_use_case = providers.Factory(
        GetMoodHistoryUseCase, mood_history_repository=mood_history_repository
    )
    update_mood_history_use_case = providers.Factory(
        UpdateMoodHistoryUseCase, mood_history_repository=mood_history_repository
    )
    delete_mood_history_use_case = providers.Factory(
        DeleteMoodHistoryUseCase, mood_history_repository=mood_history_repository
    )

    # User Friends use cases
    list_user_friends_use_case = providers.Factory(
        ListUserFriendsUseCase, user_friends_repository=user_friends_repository
    )
    get_user_friend_use_case = providers.Factory(
        GetUserFriendUseCase, user_friends_repository=user_friends_repository
    )
    add_friend_use_case = providers.Factory(
        AddFriendUseCase, user_friends_repository=user_friends_repository
    )
    update_user_friend_use_case = providers.Factory(
        UpdateUserFriendUseCase, user_friends_repository=user_friends_repository
    )
    remove_friend_use_case = providers.Factory(
        RemoveFriendUseCase, user_friends_repository=user_friends_repository
    )

    # Character Items use cases
    list_character_items_use_case = providers.Factory(
        ListCharacterItemsUseCase, character_items_repository=character_items_repository
    )
    get_character_item_use_case = providers.Factory(
        GetCharacterItemUseCase, character_items_repository=character_items_repository
    )
    purchase_item_use_case = providers.Factory(
        PurchaseItemUseCase, character_items_repository=character_items_repository
    )
    update_character_item_use_case = providers.Factory(
        UpdateCharacterItemUseCase,
        character_items_repository=character_items_repository,
    )
    remove_character_item_use_case = providers.Factory(
        RemoveCharacterItemUseCase,
        character_items_repository=character_items_repository,
    )

    # Character Backgrounds use cases
    list_character_backgrounds_use_case = providers.Factory(
        ListCharacterBackgroundsUseCase,
        character_backgrounds_repository=character_backgrounds_repository,
    )
    get_character_background_use_case = providers.Factory(
        GetCharacterBackgroundUseCase,
        character_backgrounds_repository=character_backgrounds_repository,
    )
    purchase_background_use_case = providers.Factory(
        PurchaseBackgroundUseCase,
        character_backgrounds_repository=character_backgrounds_repository,
    )
    update_character_background_use_case = providers.Factory(
        UpdateCharacterBackgroundUseCase,
        character_backgrounds_repository=character_backgrounds_repository,
    )
    remove_character_background_use_case = providers.Factory(
        RemoveCharacterBackgroundUseCase,
        character_backgrounds_repository=character_backgrounds_repository,
    )

    # Item Categories use cases
    list_item_categories_use_case = providers.Factory(
        ListItemCategoriesUseCase, item_categories_repository=item_categories_repository
    )
    get_item_category_use_case = providers.Factory(
        GetItemCategoryUseCase, item_categories_repository=item_categories_repository
    )
    create_item_category_use_case = providers.Factory(
        CreateItemCategoryUseCase, item_categories_repository=item_categories_repository
    )
    update_item_category_use_case = providers.Factory(
        UpdateItemCategoryUseCase, item_categories_repository=item_categories_repository
    )
    delete_item_category_use_case = providers.Factory(
        DeleteItemCategoryUseCase, item_categories_repository=item_categories_repository
    )

    # Item Background Positions use cases
    list_positions_for_item_use_case = providers.Factory(
        ListPositionsForItemUseCase,
        positions_repository=item_background_positions_repository,
    )
    get_position_use_case = providers.Factory(
        GetPositionUseCase, positions_repository=item_background_positions_repository
    )
    create_position_use_case = providers.Factory(
        CreatePositionUseCase, positions_repository=item_background_positions_repository
    )
    update_position_use_case = providers.Factory(
        UpdatePositionUseCase, positions_repository=item_background_positions_repository
    )
    delete_position_use_case = providers.Factory(
        DeletePositionUseCase, positions_repository=item_background_positions_repository
    )
