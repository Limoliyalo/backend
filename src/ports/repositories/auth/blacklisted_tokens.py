"""Port for blacklisted tokens repository."""

from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from src.domain.entities.auth import BlacklistedToken


class BlacklistedTokensRepository(ABC):
    """Repository for managing blacklisted access tokens."""

    @abstractmethod
    async def add(self, token: BlacklistedToken) -> BlacklistedToken:
        """Add a token to the blacklist."""
        ...

    @abstractmethod
    async def is_blacklisted(self, jti: UUID) -> bool:
        """Check if a token JTI is blacklisted."""
        ...

    @abstractmethod
    async def blacklist_all_for_user(
        self, user_tg_id: int, reason: str, expires_at: datetime
    ) -> None:
        """
        Blacklist all active tokens for a user.

        Note: This is a simplified approach. In production, you might want to
        store active tokens and blacklist them individually.
        """
        ...

    @abstractmethod
    async def cleanup_expired(self) -> int:
        """Remove expired tokens from blacklist. Returns count of removed tokens."""
        ...
