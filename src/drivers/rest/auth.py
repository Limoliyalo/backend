import logging

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, status

from src.container import ApplicationContainer
from src.core.auth.dependencies import (
    get_telegram_auth_data,
    get_telegram_current_user,
)
from src.core.auth.schemas.tma import TelegramAuthData
from src.domain.value_objects.telegram_id import TelegramId
from src.drivers.rest.schemas.auth import (
    TelegramAuthDataResponse,
    TelegramUserResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["Auth"])


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


def _map_telegram_auth_data(auth_data: TelegramAuthData) -> TelegramAuthDataResponse:
    """Map TelegramAuthData to TelegramAuthDataResponse."""
    return TelegramAuthDataResponse(
        user=_map_telegram_user(auth_data.user),
        auth_date=auth_data.auth_date,
    )




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
    return {
        "message": "Telegram Mini App authentication successful",
        "user_id": user_id.value,
    }
