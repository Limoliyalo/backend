from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query, status

from src.core.auth.admin import admin_user_provider
from src.core.auth.dependencies import get_telegram_current_user
from src.adapters.repositories.exceptions import (
    DuplicateEntityError,
    RepositoryError,
)
from src.container import ApplicationContainer
from src.domain.exceptions import EntityNotFoundException
from src.drivers.rest.exceptions import BadRequestException, NotFoundException
from src.drivers.rest.schemas.user_friends import (
    FriendInfoResponse,
    UserFriendAdminDelete,
    UserFriendCreate,
    UserFriendDelete,
    UserFriendResponse,
    UserFriendUpdate,
    UserFriendUserCreate,
)
from src.drivers.rest.schemas.activities import (
    BaseCharacterActivityResponse,
    MoodHistoryResponse,
)
from src.drivers.rest.schemas.character_backgrounds import CharacterBackgroundResponse
from src.drivers.rest.schemas.character_items import CharacterItemResponse
from src.drivers.rest.schemas.characters import CharacterResponse
from src.drivers.rest.schemas.transactions import TransactionResponse
from src.use_cases.user_friends.manage_user_friends import (
    AddFriendInput,
    AddFriendUseCase,
    CheckMutualFriendshipUseCase,
    GetUserFriendUseCase,
    ListUserFriendsUseCase,
    RemoveFriendUseCase,
    UpdateUserFriendInput,
    UpdateUserFriendUseCase,
)
from src.use_cases.characters.get_character import GetCharacterByUserUseCase
from src.use_cases.users.manage_users import GetUserUseCase
from src.ports.repositories.healthity.characters import (
    CharacterItemsRepository,
    CharacterBackgroundsRepository,
)
from src.ports.repositories.healthity.activities import (
    BaseCharacterActivitiesRepository,
    MoodHistoryRepository,
)
from src.ports.repositories.healthity.transactions import TransactionsRepository

router = APIRouter(prefix="/user-friends", tags=["User Friends"])


@router.get(
    "/{owner_tg_id}/admin",
    response_model=list[UserFriendResponse],
    status_code=status.HTTP_200_OK,
)
@inject
async def list_user_friends(
    owner_tg_id: int,
    _: int = Depends(admin_user_provider),
    use_case: ListUserFriendsUseCase = Depends(
        Provide[ApplicationContainer.list_user_friends_use_case]
    ),
):
    """Получить список друзей пользователя (требуется админ-доступ)"""
    friends = await use_case.execute(owner_tg_id)
    return [
        UserFriendResponse(
            id=f.id,
            owner_tg_id=f.owner_tg_id,
            friend_tg_id=f.friend_tg_id,
            created_at=f.created_at,
        )
        for f in friends
    ]


@router.get("/id/{friend_id}/admin", response_model=UserFriendResponse)
@inject
async def get_user_friend(
    friend_id: UUID,
    _: int = Depends(admin_user_provider),
    use_case: GetUserFriendUseCase = Depends(
        Provide[ApplicationContainer.get_user_friend_use_case]
    ),
):
    """Получить запись друга по ID (требуется админ-доступ)"""
    try:
        friend = await use_case.execute(friend_id)
        return UserFriendResponse(
            id=friend.id,
            owner_tg_id=friend.owner_tg_id,
            friend_tg_id=friend.friend_tg_id,
            created_at=friend.created_at,
        )
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))


@router.post(
    "/admin",
    response_model=UserFriendResponse,
    status_code=status.HTTP_201_CREATED,
)
@inject
async def add_friend(
    data: UserFriendCreate,
    _: int = Depends(admin_user_provider),
    use_case: AddFriendUseCase = Depends(
        Provide[ApplicationContainer.add_friend_use_case]
    ),
):
    """Добавить друга (требуется админ-доступ)"""
    try:
        input_data = AddFriendInput(
            owner_tg_id=data.owner_tg_id, friend_tg_id=data.friend_tg_id
        )
        friend = await use_case.execute(input_data)
        return UserFriendResponse(
            id=friend.id,
            owner_tg_id=friend.owner_tg_id,
            friend_tg_id=friend.friend_tg_id,
            created_at=friend.created_at,
        )
    except DuplicateEntityError:
        raise BadRequestException(detail="This user is already in the friend list")
    except ValueError as e:
        raise BadRequestException(detail=str(e))


@router.patch("/admin", response_model=UserFriendResponse)
@inject
async def update_user_friend(
    data: UserFriendUpdate,
    _: int = Depends(admin_user_provider),
    use_case: UpdateUserFriendUseCase = Depends(
        Provide[ApplicationContainer.update_user_friend_use_case]
    ),
):
    """Обновить запись друга (требуется админ-доступ)"""
    try:
        input_data = UpdateUserFriendInput(
            friend_id=data.friend_id, friend_tg_id=data.friend_tg_id
        )
        friend = await use_case.execute(input_data)
        return UserFriendResponse(
            id=friend.id,
            owner_tg_id=friend.owner_tg_id,
            friend_tg_id=friend.friend_tg_id,
            created_at=friend.created_at,
        )
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))


@router.delete(
    "/admin",
    status_code=status.HTTP_204_NO_CONTENT,
)
@inject
async def remove_friend(
    data: UserFriendAdminDelete,
    _: int = Depends(admin_user_provider),
    use_case: RemoveFriendUseCase = Depends(
        Provide[ApplicationContainer.remove_friend_use_case]
    ),
):
    """Удалить друга (требуется админ-доступ)"""
    try:
        await use_case.execute(data.owner_tg_id, data.friend_tg_id)
    except RepositoryError as e:
        raise NotFoundException(detail=str(e))


@router.get("/me", response_model=list[UserFriendResponse])
@inject
async def list_my_friends(
    telegram_id: int = Depends(get_telegram_current_user),
    use_case: ListUserFriendsUseCase = Depends(
        Provide[ApplicationContainer.list_user_friends_use_case]
    ),
):
    """Получить список своих друзей"""

    friends = await use_case.execute(telegram_id)
    return [
        UserFriendResponse(
            id=friend.id,
            owner_tg_id=friend.owner_tg_id,
            friend_tg_id=friend.friend_tg_id,
            created_at=friend.created_at,
        )
        for friend in friends
    ]


@router.post(
    "/me", response_model=UserFriendResponse, status_code=status.HTTP_201_CREATED
)
@inject
async def add_my_friend(
    data: UserFriendUserCreate,
    telegram_id: int = Depends(get_telegram_current_user),
    use_case: AddFriendUseCase = Depends(
        Provide[ApplicationContainer.add_friend_use_case]
    ),
):
    """Добавить друга"""

    try:
        input_data = AddFriendInput(
            owner_tg_id=telegram_id, friend_tg_id=data.friend_tg_id
        )
        friend = await use_case.execute(input_data)
        return UserFriendResponse(
            id=friend.id,
            owner_tg_id=friend.owner_tg_id,
            friend_tg_id=friend.friend_tg_id,
            created_at=friend.created_at,
        )
    except DuplicateEntityError:
        raise BadRequestException(detail="This user is already in your friends list")
    except ValueError as e:
        raise BadRequestException(detail=str(e))


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def remove_my_friend(
    data: UserFriendDelete,
    telegram_id: int = Depends(get_telegram_current_user),
    use_case: RemoveFriendUseCase = Depends(
        Provide[ApplicationContainer.remove_friend_use_case]
    ),
):
    """Удалить друга из своего списка"""

    try:
        await use_case.execute(telegram_id, data.friend_tg_id)
    except RepositoryError as e:
        raise NotFoundException(detail=str(e))


@router.get("/me/friend", response_model=FriendInfoResponse)
@inject
async def get_friend_info(
    friend_tg_id: int = Query(..., description="Telegram ID друга"),
    telegram_id: int = Depends(get_telegram_current_user),
    check_mutual_friendship_use_case: CheckMutualFriendshipUseCase = Depends(
        Provide[ApplicationContainer.check_mutual_friendship_use_case]
    ),
    get_user_use_case: GetUserUseCase = Depends(
        Provide[ApplicationContainer.get_user_use_case]
    ),
    get_character_use_case: GetCharacterByUserUseCase = Depends(
        Provide[ApplicationContainer.get_character_by_user_use_case]
    ),
    items_repo: CharacterItemsRepository = Depends(
        Provide[ApplicationContainer.character_items_repository]
    ),
    backgrounds_repo: CharacterBackgroundsRepository = Depends(
        Provide[ApplicationContainer.character_backgrounds_repository]
    ),
    mood_repo: MoodHistoryRepository = Depends(
        Provide[ApplicationContainer.mood_history_repository]
    ),
    transactions_repo: TransactionsRepository = Depends(
        Provide[ApplicationContainer.transactions_repository]
    ),
    base_activities_repo: BaseCharacterActivitiesRepository = Depends(
        Provide[ApplicationContainer.base_character_activities_repository]
    ),
):
    """Получить полную информацию о друге (требуется взаимная дружба)"""
    try:
        # Проверяем взаимную дружбу - обе стороны должны добавить друг друга
        is_mutual_friend = await check_mutual_friendship_use_case.execute(
            user1_tg_id=telegram_id, user2_tg_id=friend_tg_id
        )
        if not is_mutual_friend:
            raise BadRequestException(
                detail="Дружба не взаимна. Оба пользователя должны добавить друг друга в друзья."
            )

        character = None
        character_items = []
        character_backgrounds = []
        base_activities = []
        mood_history = []
        transactions = []

        try:
            friend_character = await get_character_use_case.execute(friend_tg_id)
            character = CharacterResponse.model_validate(friend_character).model_dump()

            character_id = friend_character.id

            # Получаем все items
            items = await items_repo.list_for_character(character_id)
            character_items = [
                CharacterItemResponse.model_validate(item).model_dump()
                for item in items
            ]

            # Получаем все backgrounds
            backgrounds = await backgrounds_repo.list_for_character(character_id)
            character_backgrounds = [
                CharacterBackgroundResponse.model_validate(bg).model_dump()
                for bg in backgrounds
            ]

            # Получаем все base activities
            activities = await base_activities_repo.list_for_character(character_id)
            base_activities = [
                BaseCharacterActivityResponse.model_validate(act).model_dump()
                for act in activities
            ]

            # Получаем mood history
            mood_entries = await mood_repo.list_for_character(character_id, limit=10000)
            mood_history = [
                MoodHistoryResponse.model_validate(mood).model_dump()
                for mood in mood_entries
            ]

        except EntityNotFoundException:
            pass  # No character found for friend

        # Получаем transactions
        transactions_list = await transactions_repo.list_for_user(friend_tg_id)
        transactions = [
            TransactionResponse.model_validate(t).model_dump()
            for t in transactions_list
        ]

        return FriendInfoResponse(
            user_tg_id=friend_tg_id,
            character=character,
            character_items=character_items,
            character_backgrounds=character_backgrounds,
            base_activities=base_activities,
            mood_history=mood_history,
            transactions=transactions,
        )
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))
    except ValueError as e:
        raise BadRequestException(detail=str(e))
