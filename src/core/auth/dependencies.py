"""FastAPI dependencies for authentication."""

from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import Depends, Request
from src.core.auth.providers import TelegramMiniAppAuthProvider
from src.container import ApplicationContainer
from src.core.auth.schemas.tma import TelegramAuthData
from src.domain.exceptions import InvalidTokenException
from src.domain.value_objects.telegram_id import TelegramId


@inject
async def get_telegram_auth_data(
    request: Request,
    tma_auth=Depends(Provide[ApplicationContainer.tma_auth]),  # провайдер из контейнера
) -> TelegramAuthData:
    """
    Валидирует Authorization: (tma|Bearer)? <initDataRaw>
    Возвращает TelegramAuthData или 401.
    """
    provider = TelegramMiniAppAuthProvider(tma_auth)
    return await provider(request)


@inject
async def get_telegram_current_user(
    auth_data: TelegramAuthData = Depends(get_telegram_auth_data),
) -> TelegramId:
    if not auth_data.user:
        raise InvalidTokenException("No user data in Telegram Mini App init data")
    return TelegramId(auth_data.user.id)
