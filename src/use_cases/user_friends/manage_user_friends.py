import uuid
from dataclasses import dataclass

from src.domain.entities.healthity.users import UserFriend
from src.domain.exceptions import EntityNotFoundException
from src.ports.repositories.healthity.users import UserFriendsRepository


@dataclass
class AddFriendInput:
    owner_tg_id: int
    friend_tg_id: int


class ListUserFriendsUseCase:
    def __init__(self, user_friends_repository: UserFriendsRepository) -> None:
        self._user_friends_repository = user_friends_repository

    async def execute(self, owner_tg_id: int) -> list[UserFriend]:
        return await self._user_friends_repository.list_for_user(owner_tg_id)


class ListIncomingFriendRequestsUseCase:
    def __init__(self, user_friends_repository: UserFriendsRepository) -> None:
        self._user_friends_repository = user_friends_repository

    async def execute(self, user_tg_id: int) -> list[UserFriend]:
        return await self._user_friends_repository.list_incoming_pending(user_tg_id)


class GetUserFriendUseCase:
    def __init__(self, user_friends_repository: UserFriendsRepository) -> None:
        self._user_friends_repository = user_friends_repository

    async def execute(self, friend_id: uuid.UUID) -> UserFriend:
        friend = await self._user_friends_repository.get_by_id(friend_id)
        if friend is None:
            raise EntityNotFoundException(f"UserFriend {friend_id} not found")
        return friend


class AddFriendUseCase:
    def __init__(self, user_friends_repository: UserFriendsRepository) -> None:
        self._user_friends_repository = user_friends_repository

    async def execute(self, data: AddFriendInput) -> UserFriend:
        friend = UserFriend(
            id=uuid.uuid4(),
            owner_tg_id=data.owner_tg_id,
            friend_tg_id=data.friend_tg_id,
        )
        return await self._user_friends_repository.add(friend)


@dataclass
class UpdateUserFriendInput:
    friend_id: uuid.UUID
    friend_tg_id: int


class UpdateUserFriendUseCase:
    def __init__(self, user_friends_repository: UserFriendsRepository) -> None:
        self._user_friends_repository = user_friends_repository

    async def execute(self, data: UpdateUserFriendInput) -> UserFriend:
        friend = await self._user_friends_repository.get_by_id(data.friend_id)
        if friend is None:
            raise EntityNotFoundException(f"UserFriend {data.friend_id} not found")

        friend.friend_tg_id = data.friend_tg_id
        return await self._user_friends_repository.update(friend)


class RemoveFriendUseCase:
    def __init__(self, user_friends_repository: UserFriendsRepository) -> None:
        self._user_friends_repository = user_friends_repository

    async def execute(self, owner_tg_id: int, friend_tg_id: int) -> None:
        await self._user_friends_repository.remove(owner_tg_id, friend_tg_id)


class AcceptIncomingFriendRequestUseCase:
    def __init__(self, user_friends_repository: UserFriendsRepository) -> None:
        self._user_friends_repository = user_friends_repository

    async def execute(self, user_tg_id: int, requester_tg_id: int) -> UserFriend:
        if user_tg_id == requester_tg_id:
            raise ValueError("Cannot accept friend request from yourself")

        incoming = await self._user_friends_repository.get_by_pair(
            owner_tg_id=requester_tg_id,
            friend_tg_id=user_tg_id,
        )
        if incoming is None:
            raise EntityNotFoundException("Incoming friend request not found")

        existing_friendship = await self._user_friends_repository.get_by_pair(
            owner_tg_id=user_tg_id,
            friend_tg_id=requester_tg_id,
        )
        if existing_friendship is not None:
            return existing_friendship

        friend = UserFriend(
            id=uuid.uuid4(),
            owner_tg_id=user_tg_id,
            friend_tg_id=requester_tg_id,
        )
        return await self._user_friends_repository.add(friend)


class DeclineIncomingFriendRequestUseCase:
    def __init__(self, user_friends_repository: UserFriendsRepository) -> None:
        self._user_friends_repository = user_friends_repository

    async def execute(self, user_tg_id: int, requester_tg_id: int) -> None:
        incoming_exists = await self._user_friends_repository.exists_pair(
            owner_tg_id=requester_tg_id,
            friend_tg_id=user_tg_id,
        )
        outgoing_exists = await self._user_friends_repository.exists_pair(
            owner_tg_id=user_tg_id,
            friend_tg_id=requester_tg_id,
        )
        if not incoming_exists or outgoing_exists:
            raise EntityNotFoundException("Incoming friend request not found")

        await self._user_friends_repository.remove_incoming_request(
            user_tg_id=user_tg_id,
            requester_tg_id=requester_tg_id,
        )


class CheckMutualFriendshipUseCase:
    """Проверяет взаимную дружбу между двумя пользователями"""

    def __init__(self, user_friends_repository: UserFriendsRepository) -> None:
        self._user_friends_repository = user_friends_repository

    async def execute(self, user1_tg_id: int, user2_tg_id: int) -> bool:
        """
        Проверяет, что обе стороны добавили друг друга в друзья.
        Возвращает True только если user1 добавил user2 И user2 добавил user1.
        """
        # Проверяем, что user1 добавил user2
        user1_friends = await self._user_friends_repository.list_for_user(user1_tg_id)
        user1_added_user2 = any(f.friend_tg_id == user2_tg_id for f in user1_friends)

        # Проверяем, что user2 добавил user1
        user2_friends = await self._user_friends_repository.list_for_user(user2_tg_id)
        user2_added_user1 = any(f.friend_tg_id == user1_tg_id for f in user2_friends)

        # Возвращаем True только если обе стороны добавили друг друга
        return user1_added_user2 and user2_added_user1
