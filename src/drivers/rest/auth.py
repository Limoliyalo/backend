import logging
from typing import Any

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, status, Security
from fastapi.security import HTTPBearer

from src.container import ApplicationContainer
from src.core.auth.dependencies import (
    get_access_token_payload,
    get_telegram_auth_data,
    get_telegram_current_user,
)
from src.core.auth.jwt_service import TokenPayload
from src.core.auth.schemas.tma import TelegramAuthData
from src.domain.value_objects.telegram_id import TelegramId
from src.adapters.repositories.exceptions import RepositoryError
from src.drivers.rest.exceptions import UnauthorizedException, BadRequestException
from src.drivers.rest.schemas.auth import (
    AuthTokensResponse,
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    TelegramAuthDataResponse,
    TelegramUserResponse,
    TelegramChatResponse,
    TelegramChatMemberResponse,
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

# Security schemes
jwt_bearer = HTTPBearer(auto_error=False)
jwt_security = HTTPBearer(scheme_name="BearerAuth", auto_error=False)

# For Telegram Mini App, we need to use HTTPBearer with custom scheme name
telegram_security = HTTPBearer(scheme_name="TelegramMiniAppAuth", auto_error=False)


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

    if isinstance(exc, RepositoryError):
        raise BadRequestException(detail=str(exc)) from exc

    raise exc


def _map_telegram_user(user) -> TelegramUserResponse | None:
    """Map TelegramUser to TelegramUserResponse."""
    if not user:
        return None
    return TelegramUserResponse(
        id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        username=user.username,
        language_code=user.language_code,
        is_premium=user.is_premium,
        photo_url=user.photo_url,
    )


def _map_telegram_chat(chat) -> TelegramChatResponse | None:
    """Map TelegramChat to TelegramChatResponse."""
    if not chat:
        return None
    return TelegramChatResponse(
        id=chat.id,
        type=chat.type,
        title=chat.title,
        username=chat.username,
        photo_url=chat.photo_url,
    )


def _map_telegram_chat_member(chat_member) -> TelegramChatMemberResponse | None:
    """Map TelegramChatMember to TelegramChatMemberResponse."""
    if not chat_member:
        return None
    return TelegramChatMemberResponse(
        status=chat_member.status,
        user=_map_telegram_user(chat_member.user),
        is_anonymous=chat_member.is_anonymous,
        custom_title=chat_member.custom_title,
    )


def _map_telegram_auth_data(auth_data: TelegramAuthData) -> TelegramAuthDataResponse:
    """Map TelegramAuthData to TelegramAuthDataResponse."""
    return TelegramAuthDataResponse(
        user=_map_telegram_user(auth_data.user),
        chat=_map_telegram_chat(auth_data.chat),
        chat_member=_map_telegram_chat_member(auth_data.chat_member),
        chat_type=auth_data.chat_type,
        auth_date=auth_data.auth_date,
        start_param=auth_data.start_param,
        can_send_after=auth_data.can_send_after,
    )


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
    except Exception as exc:
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
    except Exception as exc:
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
    except Exception as exc:
        _handle_auth_error(exc)


@router.get(
    "/protected",
    dependencies=[Security(jwt_security)],
    responses={
        200: {"description": "JWT claims successfully retrieved"},
        401: {"description": "Invalid or expired JWT token"},
    },
)
async def protected(
    payload: TokenPayload = Depends(get_access_token_payload),
):
    """Protected endpoint for testing JWT authentication with blacklist checking."""
    claims: dict[str, Any] = dict(payload.claims)
    return claims


@router.get(
    "/telegram/me",
    response_model=TelegramAuthDataResponse,
    responses={
        200: {"description": "Telegram user data successfully retrieved"},
        401: {"description": "Invalid Telegram Mini App init data"},
    },
)
async def get_telegram_me(
    auth_data: TelegramAuthData = Depends(get_telegram_auth_data),
):
    return _map_telegram_auth_data(auth_data)

@router.get(
    "/telegram/user-id",
    responses={
        200: {"description": "Telegram user ID successfully retrieved"},
        401: {"description": "Invalid Telegram Mini App init data"},
    },
)
async def get_telegram_user_id(
    user_id: TelegramId = Depends(get_telegram_current_user),
):
    return {"user_id": user_id.value}


@router.get(
    "/telegram/protected",
    responses={
        200: {"description": "Telegram Mini App authentication successful"},
        401: {"description": "Invalid Telegram Mini App init data"},
    },
)
async def telegram_protected(
    user_id: TelegramId = Depends(get_telegram_current_user),
):
    return {"message": "Telegram Mini App authentication successful", "user_id": user_id.value}
