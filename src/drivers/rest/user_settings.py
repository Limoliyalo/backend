from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, status

from src.container import ApplicationContainer
from src.core.auth.dependencies import get_telegram_current_user
from src.domain.exceptions import EntityNotFoundException
from src.domain.value_objects.telegram_id import TelegramId
from src.adapters.repositories.exceptions import RepositoryError
from src.drivers.rest.exceptions import NotFoundException, BadRequestException
from src.drivers.rest.schemas.user_settings import (
    UserSettingsResponse,
    UserSettingsUpdate,
)
from src.use_cases.user_settings.manage_settings import (
    DeleteUserSettingsUseCase,
    GetUserSettingsUseCase,
    PatchUserSettingsUseCase,
)

router = APIRouter(prefix="/user-settings", tags=["User Settings"])


@router.get("/me", response_model=UserSettingsResponse)
@inject
async def get_my_settings(
    telegram_id: TelegramId = Depends(get_telegram_current_user),
    use_case: GetUserSettingsUseCase = Depends(
        Provide[ApplicationContainer.get_user_settings_use_case]
    ),
):
    """Получить настройки текущего пользователя"""
    try:
        settings = await use_case.execute(telegram_id.value)
        return UserSettingsResponse.model_validate(settings)
    except RepositoryError as e:
        raise BadRequestException(detail=str(e))
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))


@router.patch("/me", response_model=UserSettingsResponse)
@inject
async def update_my_settings(
    data: UserSettingsUpdate,
    telegram_id: TelegramId = Depends(get_telegram_current_user),
    use_case: PatchUserSettingsUseCase = Depends(
        Provide[ApplicationContainer.patch_user_settings_use_case]
    ),
):
    """Обновить настройки текущего пользователя"""
    input_data = data.to_patch_input(telegram_id.value)
    try:
        settings = await use_case.execute(input_data)
        return UserSettingsResponse.model_validate(settings)
    except RepositoryError as e:
        raise BadRequestException(detail=str(e))


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_my_settings(
    telegram_id: TelegramId = Depends(get_telegram_current_user),
    use_case: DeleteUserSettingsUseCase = Depends(
        Provide[ApplicationContainer.delete_user_settings_use_case]
    ),
):
    """Удалить настройки текущего пользователя"""
    try:
        await use_case.execute(telegram_id.value)
    except RepositoryError as e:
        raise BadRequestException(detail=str(e))
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))
