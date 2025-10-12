import logging
from typing import Any

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, status

from src.container import ApplicationContainer
from src.core.auth.dependencies import get_access_token_payload
from src.core.auth.jwt_service import TokenPayload
from src.drivers.rest.exceptions import UnauthorizedException
from src.drivers.rest.schemas.auth import (
    AuthTokensResponse,
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
)
from src.domain.exceptions import (
    InactiveUserException,
    InvalidCredentialsException,
    InvalidTokenException,
    RefreshTokenNotFoundException,
    RefreshTokenRevokedException,
    TokenExpiredException,
    UserNotFoundException,
)
from src.use_cases.auth import (
    AuthTokens,
    LoginInput,
    LoginUseCase,
    LogoutInput,
    LogoutUseCase,
    RefreshInput,
    RefreshUseCase,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["Auth"])


def _map_tokens(tokens: AuthTokens) -> AuthTokensResponse:
    return AuthTokensResponse(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
        token_type=tokens.token_type,
        expires_in=tokens.expires_in,
        refresh_expires_in=tokens.refresh_expires_in,
        access_token_expires_at=tokens.access_token_expires_at,
        refresh_token_expires_at=tokens.refresh_token_expires_at,
    )


def _handle_auth_error(exc: Exception) -> None:
    unauthorized_errors = (
        InvalidCredentialsException,
        InvalidTokenException,
        RefreshTokenNotFoundException,
        RefreshTokenRevokedException,
        TokenExpiredException,
        UserNotFoundException,
        InactiveUserException,
    )

    if isinstance(exc, unauthorized_errors):
        raise UnauthorizedException(detail=str(exc)) from exc

    raise exc


@router.post(
    "/login", response_model=AuthTokensResponse, status_code=status.HTTP_200_OK
)
@inject
async def login(
    payload: LoginRequest,
    use_case: LoginUseCase = Depends(Provide[ApplicationContainer.login_use_case]),
):
    logger.info(
        {
            "action": "auth.login",
            "stage": "start",
            "data": {"user_tg_id": payload.user_tg_id},
        }
    )

    try:
        tokens = await use_case.execute(
            LoginInput(user_tg_id=payload.user_tg_id, password=payload.password)
        )
        return _map_tokens(tokens)
    except Exception as exc:  # pragma: no cover - safety net
        logger.warning(
            {
                "action": "auth.login",
                "stage": "failed",
                "data": {"user_tg_id": payload.user_tg_id, "reason": str(exc)},
            }
        )
        _handle_auth_error(exc)


@router.post(
    "/refresh", response_model=AuthTokensResponse, status_code=status.HTTP_200_OK
)
@inject
async def refresh(
    payload: RefreshRequest,
    use_case: RefreshUseCase = Depends(Provide[ApplicationContainer.refresh_use_case]),
):
    try:
        tokens = await use_case.execute(
            RefreshInput(refresh_token=payload.refresh_token)
        )
        return _map_tokens(tokens)
    except Exception as exc:  # pragma: no cover - safety net
        _handle_auth_error(exc)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def logout(
    payload: LogoutRequest,
    use_case: LogoutUseCase = Depends(Provide[ApplicationContainer.logout_use_case]),
):
    try:
        await use_case.execute(
            LogoutInput(
                refresh_token=payload.refresh_token,
                access_token=payload.access_token,
                revoke_all=payload.revoke_all,
            )
        )
    except Exception as exc:  # pragma: no cover - safety net
        _handle_auth_error(exc)


@router.get("/protected")
async def protected(
    payload: TokenPayload = Depends(get_access_token_payload),
):
    """Protected endpoint for testing JWT authentication with blacklist checking."""
    claims: dict[str, Any] = dict(payload.claims)
    return claims
