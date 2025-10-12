from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.auth import RefreshToken
from src.domain.value_objects.telegram_id import TelegramId


class RefreshTokensRepository(ABC):
    @abstractmethod
    async def create(self, token: RefreshToken) -> RefreshToken:
        raise NotImplementedError

    @abstractmethod
    async def get_by_jti(self, jti: UUID) -> RefreshToken | None:
        raise NotImplementedError

    @abstractmethod
    async def save(self, token: RefreshToken) -> RefreshToken:
        """Persist state changes for existing token."""
        raise NotImplementedError

    @abstractmethod
    async def revoke_for_user(self, user_tg_id: TelegramId) -> None:
        """Revoke all refresh tokens for user (e.g., on logout everywhere)."""
        raise NotImplementedError
