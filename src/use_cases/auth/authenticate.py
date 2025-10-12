from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID, uuid4

from src.core.auth.jwt_service import JwtService, TokenType
from src.core.security import PasswordHasher, TokenHasher
from src.domain.entities.auth import RefreshToken
from src.domain.entities.healthity.users import User
from src.domain.exceptions import (
    InactiveUserException,
    InvalidCredentialsException,
    InvalidTokenException,
    RefreshTokenNotFoundException,
    RefreshTokenRevokedException,
    TokenExpiredException,
    UserNotFoundException,
)
from src.domain.value_objects.telegram_id import TelegramId
from src.ports.repositories.auth import (
    BlacklistedTokensRepository,
    RefreshTokensRepository,
)
from src.ports.repositories.users import UsersRepository


logger = logging.getLogger(__name__)


@dataclass
class AuthTokens:
    access_token: str
    refresh_token: str
    token_type: str
    access_token_expires_at: datetime
    refresh_token_expires_at: datetime
    expires_in: int
    refresh_expires_in: int
    refresh_token_jti: UUID


@dataclass
class LoginInput:
    user_tg_id: int
    password: str


@dataclass
class RefreshInput:
    refresh_token: str


@dataclass
class LogoutInput:
    refresh_token: str
    access_token: str | None = None
    revoke_all: bool = False


class _TokenFactory:
    def __init__(self, jwt_service: JwtService) -> None:
        self._jwt_service = jwt_service

    def create_tokens(self, *, subject: int, claims: dict[str, object]) -> AuthTokens:
        access_token, access_exp, _ = self._jwt_service.create_access_token(
            subject=subject, additional_claims=claims
        )
        refresh_token, refresh_exp, refresh_jti = (
            self._jwt_service.create_refresh_token(
                subject=subject, additional_claims=claims
            )
        )

        now = datetime.now(tz=timezone.utc)
        access_expires_in = max(int((access_exp - now).total_seconds()), 0)
        refresh_expires_in = max(int((refresh_exp - now).total_seconds()), 0)

        return AuthTokens(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            access_token_expires_at=access_exp,
            refresh_token_expires_at=refresh_exp,
            expires_in=access_expires_in,
            refresh_expires_in=refresh_expires_in,
            refresh_token_jti=refresh_jti,
        )


class _RefreshTokenManager:
    def __init__(
        self,
        repository: RefreshTokensRepository,
        token_hasher: TokenHasher,
        jwt_service: JwtService,
    ) -> None:
        self._repository = repository
        self._token_hasher = token_hasher
        self._jwt_service = jwt_service

    async def persist_new(
        self,
        *,
        user: User,
        refresh_token: str,
        expires_at: datetime,
        jti: UUID,
    ) -> RefreshToken:
        entity = RefreshToken(
            id=uuid4(),
            user_tg_id=user.telegram_id,
            token_hash=self._token_hasher.hash_token(refresh_token),
            jti=jti,
            expires_at=expires_at,
        )
        stored = await self._repository.create(entity)
        logger.debug(
            {
                "action": "RefreshTokenManager.persist_new",
                "stage": "stored",
                "data": {
                    "user_tg_id": user.telegram_id.value,
                    "refresh_jti": str(jti),
                },
            }
        )
        return stored

    async def revoke(self, token: RefreshToken) -> RefreshToken:
        token.revoke()
        updated = await self._repository.save(token)
        logger.debug(
            {
                "action": "RefreshTokenManager.revoke",
                "stage": "revoked",
                "data": {
                    "refresh_jti": str(token.jti),
                },
            }
        )
        return updated

    async def revoke_all(self, telegram_id: TelegramId) -> None:
        await self._repository.revoke_for_user(telegram_id)
        logger.debug(
            {
                "action": "RefreshTokenManager.revoke_all",
                "data": {"user_tg_id": telegram_id.value},
            }
        )

    async def validate(self, *, refresh_token: str) -> tuple[RefreshToken, int]:
        payload = self._jwt_service.decode(
            refresh_token, expected_type=TokenType.REFRESH
        )
        token = await self._repository.get_by_jti(payload.jti)

        if token is None:
            logger.debug(
                {
                    "action": "RefreshTokenManager.validate",
                    "stage": "not_found",
                    "data": {"jti": str(payload.jti)},
                }
            )
            raise RefreshTokenNotFoundException(str(payload.jti))

        if token.revoked:
            raise RefreshTokenRevokedException(str(payload.jti))

        if token.expires_at < datetime.now(tz=timezone.utc):
            raise TokenExpiredException()

        if not self._token_hasher.verify(refresh_token, token.token_hash):
            raise InvalidTokenException("Refresh token mismatch")

        try:
            user_id = int(payload.sub)
        except (TypeError, ValueError) as exc:
            raise InvalidTokenException("Invalid subject claim") from exc

        if token.user_tg_id.value != user_id:
            raise InvalidTokenException("Token subject mismatch")

        return token, user_id


class LoginUseCase:
    def __init__(
        self,
        users_repository: UsersRepository,
        refresh_tokens_repository: RefreshTokensRepository,
        password_hasher: PasswordHasher,
        token_hasher: TokenHasher,
        jwt_service: JwtService,
    ) -> None:
        self._users_repository = users_repository
        self._password_hasher = password_hasher
        self._token_factory = _TokenFactory(jwt_service)
        self._token_manager = _RefreshTokenManager(
            refresh_tokens_repository,
            token_hasher,
            jwt_service,
        )

    async def execute(self, data: LoginInput) -> AuthTokens:
        telegram_id = TelegramId(data.user_tg_id)
        user = await self._users_repository.get_by_telegram_id(telegram_id)

        if user is None or not user.password_hash:
            raise InvalidCredentialsException()

        if not self._password_hasher.verify_password(data.password, user.password_hash):
            raise InvalidCredentialsException()

        if not user.is_active:
            raise InactiveUserException(data.user_tg_id)

        await self._token_manager.revoke_all(user.telegram_id)

        claims = {"is_admin": user.is_admin}
        tokens = self._token_factory.create_tokens(
            subject=user.telegram_id.value,
            claims=claims,
        )

        await self._token_manager.persist_new(
            user=user,
            refresh_token=tokens.refresh_token,
            expires_at=tokens.refresh_token_expires_at,
            jti=tokens.refresh_token_jti,
        )

        logger.info(
            {
                "action": "LoginUseCase.execute",
                "stage": "success",
                "data": {"user_tg_id": data.user_tg_id},
            }
        )

        return tokens


class RefreshUseCase:
    def __init__(
        self,
        users_repository: UsersRepository,
        refresh_tokens_repository: RefreshTokensRepository,
        token_hasher: TokenHasher,
        jwt_service: JwtService,
    ) -> None:
        self._users_repository = users_repository
        self._token_factory = _TokenFactory(jwt_service)
        self._token_manager = _RefreshTokenManager(
            refresh_tokens_repository,
            token_hasher,
            jwt_service,
        )

    async def execute(self, data: RefreshInput) -> AuthTokens:
        token, user_id = await self._token_manager.validate(
            refresh_token=data.refresh_token
        )

        user = await self._users_repository.get_by_telegram_id(TelegramId(user_id))
        if user is None:
            raise UserNotFoundException(user_id)
        if not user.is_active:
            raise InactiveUserException(user_id)

        await self._token_manager.revoke(token)

        claims = {"is_admin": user.is_admin}
        tokens = self._token_factory.create_tokens(
            subject=user.telegram_id.value,
            claims=claims,
        )

        await self._token_manager.persist_new(
            user=user,
            refresh_token=tokens.refresh_token,
            expires_at=tokens.refresh_token_expires_at,
            jti=tokens.refresh_token_jti,
        )

        return tokens


class LogoutUseCase:
    def __init__(
        self,
        refresh_tokens_repository: RefreshTokensRepository,
        blacklisted_tokens_repository: "BlacklistedTokensRepository",
        token_hasher: TokenHasher,
        jwt_service: JwtService,
    ) -> None:
        self._token_manager = _RefreshTokenManager(
            refresh_tokens_repository,
            token_hasher,
            jwt_service,
        )
        self._blacklisted_tokens_repository = blacklisted_tokens_repository
        self._jwt_service = jwt_service

    async def execute(self, data: LogoutInput) -> None:
        token, user_id = await self._token_manager.validate(
            refresh_token=data.refresh_token
        )

        if data.revoke_all:
            await self._token_manager.revoke_all(TelegramId(user_id))
        else:
            await self._token_manager.revoke(token)

        # Blacklist the access token if provided
        if data.access_token:
            try:
                payload = self._jwt_service.decode(
                    data.access_token, expected_type=TokenType.ACCESS
                )
                from src.domain.entities.auth import BlacklistedToken

                blacklisted = BlacklistedToken(
                    jti=payload.jti,
                    user_tg_id=user_id,
                    reason="logout" if not data.revoke_all else "revoke_all",
                    blacklisted_at=datetime.now(tz=timezone.utc),
                    expires_at=payload.expires_at,
                )
                await self._blacklisted_tokens_repository.add(blacklisted)
                logger.debug(
                    {
                        "action": "LogoutUseCase.execute",
                        "stage": "access_token_blacklisted",
                        "data": {
                            "user_id": user_id,
                            "jti": str(payload.jti),
                        },
                    }
                )
            except (InvalidTokenException, TokenExpiredException) as exc:
                # If access token is invalid or expired, just log and continue
                logger.warning(
                    {
                        "action": "LogoutUseCase.execute",
                        "stage": "access_token_invalid",
                        "data": {"user_id": user_id, "error": str(exc)},
                    }
                )
