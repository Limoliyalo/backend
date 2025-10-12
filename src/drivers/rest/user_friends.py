from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, status
from src.core.auth.admin import admin_user_provider
from src.adapters.repositories.exceptions import RepositoryError
from src.container import ApplicationContainer
from src.domain.exceptions import EntityNotFoundException
from src.drivers.rest.exceptions import BadRequestException, NotFoundException
from src.drivers.rest.schemas.user_friends import (
    UserFriendCreate,
    UserFriendResponse,
    UserFriendUpdate,
)
from src.use_cases.user_friends.manage_user_friends import (
    AddFriendInput,
    AddFriendUseCase,
    GetUserFriendUseCase,
    ListUserFriendsUseCase,
    RemoveFriendUseCase,
    UpdateUserFriendInput,
    UpdateUserFriendUseCase,
)

router = APIRouter(prefix="/user-friends", tags=["User Friends"])


@router.get(
    "/admin/{owner_tg_id}",
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
            owner_tg_id=f.owner_tg_id.value,
            friend_tg_id=f.friend_tg_id.value,
            created_at=f.created_at,
        )
        for f in friends
    ]


@router.get("/id/{friend_id}", response_model=UserFriendResponse)
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
            owner_tg_id=friend.owner_tg_id.value,
            friend_tg_id=friend.friend_tg_id.value,
            created_at=friend.created_at,
        )
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))


@router.post(
    "/admin/{owner_tg_id}",
    response_model=UserFriendResponse,
    status_code=status.HTTP_201_CREATED,
)
@inject
async def add_friend(
    owner_tg_id: int,
    data: UserFriendCreate,
    _: int = Depends(admin_user_provider),
    use_case: AddFriendUseCase = Depends(
        Provide[ApplicationContainer.add_friend_use_case]
    ),
):
    """Добавить друга (требуется админ-доступ)"""
    try:
        input_data = AddFriendInput(
            owner_tg_id=owner_tg_id, friend_tg_id=data.friend_tg_id
        )
        friend = await use_case.execute(input_data)
        return UserFriendResponse(
            id=friend.id,
            owner_tg_id=friend.owner_tg_id.value,
            friend_tg_id=friend.friend_tg_id.value,
            created_at=friend.created_at,
        )
    except ValueError as e:
        raise BadRequestException(detail=str(e))


@router.patch("/id/{friend_id}", response_model=UserFriendResponse)
@inject
async def update_user_friend(
    friend_id: UUID,
    data: UserFriendUpdate,
    _: int = Depends(admin_user_provider),
    use_case: UpdateUserFriendUseCase = Depends(
        Provide[ApplicationContainer.update_user_friend_use_case]
    ),
):
    """Обновить запись друга (требуется админ-доступ)"""
    try:
        input_data = UpdateUserFriendInput(
            friend_id=friend_id, friend_tg_id=data.friend_tg_id
        )
        friend = await use_case.execute(input_data)
        return UserFriendResponse(
            id=friend.id,
            owner_tg_id=friend.owner_tg_id.value,
            friend_tg_id=friend.friend_tg_id.value,
            created_at=friend.created_at,
        )
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))


@router.delete(
    "/admin/{owner_tg_id}/friends/{friend_tg_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
@inject
async def remove_friend(
    owner_tg_id: int,
    friend_tg_id: int,
    _: int = Depends(admin_user_provider),
    use_case: RemoveFriendUseCase = Depends(
        Provide[ApplicationContainer.remove_friend_use_case]
    ),
):
    """Удалить друга (требуется админ-доступ)"""
    try:
        await use_case.execute(owner_tg_id, friend_tg_id)
    except RepositoryError as e:
        raise NotFoundException(detail=str(e))
