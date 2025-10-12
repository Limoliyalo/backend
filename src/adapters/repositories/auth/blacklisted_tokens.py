"""SQLAlchemy implementation of blacklisted tokens repository."""

import logging
from datetime import datetime
from typing import Callable
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.database.models.blacklisted_tokens import BlacklistedTokenModel
from src.adapters.database.uow import SQLAlchemyUnitOfWork
from src.domain.entities.auth import BlacklistedToken
from src.ports.repositories.auth import BlacklistedTokensRepository

logger = logging.getLogger(__name__)


class SQLAlchemyBlacklistedTokensRepository(BlacklistedTokensRepository):
    """SQLAlchemy implementation of blacklisted tokens repository."""

    def __init__(self, uow_factory: Callable[[], SQLAlchemyUnitOfWork]) -> None:
        self._uow_factory = uow_factory

    async def add(self, token: BlacklistedToken) -> BlacklistedToken:
        """Add a token to the blacklist."""
        async with self._uow_factory() as uow:
            session: AsyncSession = uow.session

            model = BlacklistedTokenModel(
                jti=token.jti,
                user_tg_id=token.user_tg_id,
                reason=token.reason,
                blacklisted_at=token.blacklisted_at,
                expires_at=token.expires_at,
            )

            session.add(model)
            await uow.commit()

            logger.debug(
                {
                    "action": "SQLAlchemyBlacklistedTokensRepository.add",
                    "stage": "success",
                    "data": {
                        "jti": str(token.jti),
                        "user_tg_id": token.user_tg_id,
                        "reason": token.reason,
                    },
                }
            )

            return BlacklistedToken(
                jti=model.jti,
                user_tg_id=model.user_tg_id,
                reason=model.reason,
                blacklisted_at=model.blacklisted_at,
                expires_at=model.expires_at,
            )

    async def is_blacklisted(self, jti: UUID) -> bool:
        """Check if a token JTI is blacklisted."""
        async with self._uow_factory() as uow:
            session: AsyncSession = uow.session

            stmt = select(BlacklistedTokenModel).where(BlacklistedTokenModel.jti == jti)
            result = await session.execute(stmt)
            exists = result.scalar_one_or_none() is not None

            logger.debug(
                {
                    "action": "SQLAlchemyBlacklistedTokensRepository.is_blacklisted",
                    "stage": "checked",
                    "data": {"jti": str(jti), "is_blacklisted": exists},
                }
            )

            return exists

    async def blacklist_all_for_user(
        self, user_tg_id: int, reason: str, expires_at: datetime
    ) -> None:
        """
        Blacklist all active tokens for a user.

        Note: This is a marker operation. In a real implementation with active
        token tracking, you would blacklist specific tokens here.
        """
        # This is intentionally a no-op because we don't track all issued tokens.
        # The revoke_all functionality is handled by refresh tokens.
        # For access tokens, we can't blacklist what we don't track.
        logger.debug(
            {
                "action": "SQLAlchemyBlacklistedTokensRepository.blacklist_all_for_user",
                "stage": "skipped",
                "data": {
                    "user_tg_id": user_tg_id,
                    "reason": "access tokens not tracked individually",
                },
            }
        )

    async def cleanup_expired(self) -> int:
        """Remove expired tokens from blacklist."""
        async with self._uow_factory() as uow:
            session: AsyncSession = uow.session

            now = datetime.now()
            stmt = delete(BlacklistedTokenModel).where(
                BlacklistedTokenModel.expires_at < now
            )
            result = await session.execute(stmt)
            await uow.commit()

            count = result.rowcount or 0

            logger.info(
                {
                    "action": "SQLAlchemyBlacklistedTokensRepository.cleanup_expired",
                    "stage": "success",
                    "data": {"removed_count": count},
                }
            )

            return count
