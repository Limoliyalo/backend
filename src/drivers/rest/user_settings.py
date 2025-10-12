from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, status

from src.container import ApplicationContainer
from src.core.auth.dependencies import get_access_token_payload
from src.core.auth.jwt_service import TokenPayload
from src.domain.exceptions import EntityNotFoundException
from src.drivers.rest.exceptions import NotFoundException
from src.drivers.rest.schemas.user_settings import (
    UserSettingsResponse,
    UserSettingsUpdate,
)
from src.use_cases.user_settings.manage_settings import (
    DeleteUserSettingsUseCase,
    GetUserSettingsUseCase,
    UpdateUserSettingsInput,
    UpsertUserSettingsUseCase,
)

router = APIRouter(prefix="/user-settings", tags=["User Settings"])


@router.get("/me", response_model=UserSettingsResponse)
@inject
async def get_my_settings(
    payload: TokenPayload = Depends(get_access_token_payload),
    use_case: GetUserSettingsUseCase = Depends(
        Provide[ApplicationContainer.get_user_settings_use_case]
    ),
):
    """Получить настройки текущего пользователя"""
    telegram_id = int(payload.sub)
    try:
        settings = await use_case.execute(telegram_id)
        return UserSettingsResponse.model_validate(settings)
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))


@router.put("/me", response_model=UserSettingsResponse)
@inject
async def update_my_settings(
    data: UserSettingsUpdate,
    payload: TokenPayload = Depends(get_access_token_payload),
    use_case: UpsertUserSettingsUseCase = Depends(
        Provide[ApplicationContainer.upsert_user_settings_use_case]
    ),
):
    """Создать или обновить настройки текущего пользователя"""
    telegram_id = int(payload.sub)
    input_data = UpdateUserSettingsInput(
        user_tg_id=telegram_id,
        quiet_start_time=data.quiet_start_time,
        quiet_end_time=data.quiet_end_time,
        muted_days=data.muted_days,
        do_not_disturb=data.do_not_disturb,
    )
    settings = await use_case.execute(input_data)
    return UserSettingsResponse.model_validate(settings)


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_my_settings(
    payload: TokenPayload = Depends(get_access_token_payload),
    use_case: DeleteUserSettingsUseCase = Depends(
        Provide[ApplicationContainer.delete_user_settings_use_case]
    ),
):
    """Удалить настройки текущего пользователя"""
    telegram_id = int(payload.sub)
    try:
        await use_case.execute(telegram_id)
    except EntityNotFoundException as e:
        raise NotFoundException(detail=str(e))
