import uuid
from dataclasses import dataclass

from src.domain.entities.healthity.users import UserFriend
from src.domain.value_objects.telegram_id import TelegramId
from src.ports.repositories.healthity.users import UserFriendsRepository


@dataclass
class AddFriendInput:
    owner_tg_id: int
    friend_tg_id: int


class ListUserFriendsUseCase:
    def __init__(self, user_friends_repository: UserFriendsRepository) -> None:
        self._user_friends_repository = user_friends_repository

    async def execute(self, owner_tg_id: int) -> list[UserFriend]:
        return await self._user_friends_repository.list_for_user(
            TelegramId(owner_tg_id)
        )


class AddFriendUseCase:
    def __init__(self, user_friends_repository: UserFriendsRepository) -> None:
        self._user_friends_repository = user_friends_repository

    async def execute(self, data: AddFriendInput) -> UserFriend:
        friend = UserFriend(
            id=uuid.uuid4(),
            owner_tg_id=TelegramId(data.owner_tg_id),
            friend_tg_id=TelegramId(data.friend_tg_id),
        )
        return await self._user_friends_repository.add(friend)


class RemoveFriendUseCase:
    def __init__(self, user_friends_repository: UserFriendsRepository) -> None:
        self._user_friends_repository = user_friends_repository

    async def execute(self, owner_tg_id: int, friend_tg_id: int) -> None:
        await self._user_friends_repository.remove(
            TelegramId(owner_tg_id), TelegramId(friend_tg_id)
        )
