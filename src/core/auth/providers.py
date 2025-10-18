import logging
from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.core.auth.jwt_service import JwtService, TokenPayload, TokenType
from src.domain.exceptions import InvalidTokenException, TokenExpiredException
from src.domain.value_objects.telegram_id import TelegramId
from src.drivers.rest.exceptions import UnauthorizedException
from src.ports.repositories.auth import BlacklistedTokensRepository

logger = logging.getLogger(__name__)
http_bearer = HTTPBearer(auto_error=False)


def _unauthorized(
    detail: str = "Could not validate credentials",
) -> UnauthorizedException:
    return UnauthorizedException(detail=detail, headers={"WWW-Authenticate": "Bearer"})


class AccessTokenPayloadProvider:
    """
    Provider for validating access tokens.

    Validates:
    1. Token exists
    2. Token is valid JWT
    3. Token is not expired
    4. Token is not blacklisted (if repository provided)
    """

    def __init__(
        self,
        jwt_service: JwtService,
        blacklisted_tokens_repository: BlacklistedTokensRepository | None = None,
    ) -> None:
        self._jwt_service = jwt_service
        self._blacklisted_tokens_repository = blacklisted_tokens_repository

    async def __call__(
        self,
        credentials: Annotated[
            HTTPAuthorizationCredentials | None,
            Depends(http_bearer),
        ],
    ) -> TokenPayload:
        if credentials is None:
            raise _unauthorized()

        token = credentials.credentials
        try:
            payload = self._jwt_service.decode(token, expected_type=TokenType.ACCESS)
        except (
            InvalidTokenException,
            TokenExpiredException,
        ) as exc:
            raise _unauthorized(str(exc)) from exc

        if self._blacklisted_tokens_repository:
            is_blacklisted = await self._blacklisted_tokens_repository.is_blacklisted(
                payload.jti
            )
            if is_blacklisted:
                logger.warning(
                    {
                        "action": "AccessTokenPayloadProvider",
                        "stage": "blacklisted",
                        "data": {"jti": str(payload.jti)},
                    }
                )
                raise _unauthorized("Token has been revoked")

        return payload


class CurrentUserProvider:
    def __init__(self, payload_provider: AccessTokenPayloadProvider) -> None:
        self._payload_provider = payload_provider

    async def __call__(
        self,
        credentials: Annotated[
            HTTPAuthorizationCredentials | None,
            Depends(http_bearer),
        ],
    ) -> TelegramId:
        payload = await self._payload_provider(credentials)

        try:
            return TelegramId(int(payload.sub))
        except (TypeError, ValueError) as exc:
            raise _unauthorized("Invalid subject claim") from exc
