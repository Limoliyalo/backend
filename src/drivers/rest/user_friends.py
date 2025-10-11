from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, status

from src.adapters.repositories.exceptions import RepositoryError
from src.container import ApplicationContainer
from src.drivers.rest.exceptions import BadRequestException, NotFoundException
from src.drivers.rest.schemas.user_friends import UserFriendCreate, UserFriendResponse
from src.use_cases.user_friends.manage_user_friends import (
    AddFriendInput,
    AddFriendUseCase,
    ListUserFriendsUseCase,
    RemoveFriendUseCase,
)

router = APIRouter(prefix="/user-friends", tags=["User Friends"])


@router.get(
    "/{owner_tg_id}",
    response_model=list[UserFriendResponse],
    status_code=status.HTTP_200_OK,
)
@inject
async def list_user_friends(
    owner_tg_id: int,
    use_case: ListUserFriendsUseCase = Depends(
        Provide[ApplicationContainer.list_user_friends_use_case]
    ),
):
    """Получить список друзей пользователя"""
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


@router.post(
    "/{owner_tg_id}",
    response_model=UserFriendResponse,
    status_code=status.HTTP_201_CREATED,
)
@inject
async def add_friend(
    owner_tg_id: int,
    data: UserFriendCreate,
    use_case: AddFriendUseCase = Depends(
        Provide[ApplicationContainer.add_friend_use_case]
    ),
):
    """Добавить друга"""
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


@router.delete(
    "/{owner_tg_id}/friends/{friend_tg_id}", status_code=status.HTTP_204_NO_CONTENT
)
@inject
async def remove_friend(
    owner_tg_id: int,
    friend_tg_id: int,
    use_case: RemoveFriendUseCase = Depends(
        Provide[ApplicationContainer.remove_friend_use_case]
    ),
):
    """Удалить друга"""
    try:
        await use_case.execute(owner_tg_id, friend_tg_id)
    except RepositoryError as e:
        raise NotFoundException(detail=str(e))
